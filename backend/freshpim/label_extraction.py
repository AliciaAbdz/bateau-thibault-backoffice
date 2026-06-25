"""
Reconnaissance d'attributs depuis une étiquette produit.

Contrainte du projet : pas de clé API, pas de modèle local possible. Le seul
moteur disponible est **Claude Code** (`claude -p`), déjà installé et authentifié
(abo de l'étudiant), gratuit et fonctionnel sur la machine.

⚠️ Piège Windows résolu : `claude` = `claude.CMD` (wrapper batch). Passer le
prompt MULTI-LIGNES en argument le fait TRONQUER par cmd.exe au premier \n →
claude ne recevait que le début et improvisait une description. On passe donc le
prompt par **stdin** (`input=`) : il arrive intact et le modèle renvoie le JSON.

Le schéma est construit DYNAMIQUEMENT depuis la famille du produit (ses
FamilyAttribute). Claude Code ne lit que dans son répertoire de travail : on
place l'image dans backend/.tmp_labels et on lance `claude` avec backend/ en cwd.

En production : remplaçable par un appel API à structured outputs (JSON garanti) ;
seule cette fonction changerait, le schéma + la validation restent identiques.
"""
import json
import os
import shutil
import subprocess
import tempfile

_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../backend
_TMP_DIR = os.path.join(_PROJECT_DIR, '.tmp_labels')


def build_schema(product):
    """Liste des champs attendus, construite depuis la famille du produit."""
    fields = []
    for fa in product.family.familyattribute_set.select_related('attribute'):
        a = fa.attribute
        field = {
            'code': a.code,
            'label': a.label,
            'type': a.type,
            'required': fa.is_required,
        }
        if a.type == 'select':
            field['options'] = a.options or []
        fields.append(field)
    return fields


def _build_prompt(image_path, fields):
    lignes = []
    for f in fields:
        desc = f"- \"{f['code']}\" ({f['label']}) : type {f['type']}"
        if f['type'] == 'select':
            desc += f", valeur OBLIGATOIREMENT l'une de {f['options']}"
        lignes.append(desc)
    squelette = json.dumps({f['code']: "" for f in fields}, ensure_ascii=False)
    return (
        f"Lis l'étiquette produit dans l'image (outil Read) : {image_path}\n"
        f"Complète ce JSON avec les valeurs lues (garde EXACTEMENT ces clés) :\n"
        f"{squelette}\n\n"
        f"Champs attendus :\n" + "\n".join(lignes) + "\n\n"
        f"Règles de valeur :\n"
        f"- Information absente de l'étiquette → \"\".\n"
        f"- number → uniquement le nombre, sans unité.\n"
        f"- select → EXACTEMENT une des valeurs autorisées, sinon \"\".\n"
        f"- bool → \"true\" ou \"false\".\n\n"
        f"Réponds UNIQUEMENT par l'objet JSON complété : commence par {{ et finis "
        f"par }}. Aucun autre texte, aucun markdown."
    )


def extract_from_image(image_bytes, fields, suffix='.jpg'):
    """Appelle le LLM et renvoie un dict {code_attribut: valeur} (valeurs brutes)."""
    os.makedirs(_TMP_DIR, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=_TMP_DIR, suffix=suffix, delete=False) as tmp:
        tmp.write(image_bytes)
        image_path = tmp.name

    try:
        prompt = _build_prompt(image_path, fields)
        claude_bin = shutil.which('claude') or 'claude'  # résout claude.cmd sous Windows
        result = subprocess.run(
            [claude_bin, '-p', '--allowedTools', 'Read'],
            input=prompt,        # ⚠️ prompt par STDIN (évite la troncature cmd.exe)
            cwd=_PROJECT_DIR,    # l'image est dans ce dossier → lecture autorisée
            capture_output=True,
            text=True,
            encoding='utf-8',    # évite le crash cp1252 sous Windows
            errors='replace',
            timeout=180,
        )
        output = (result.stdout or '').strip()
        # le modèle renvoie le JSON ; on isole le 1er objet { ... } par sécurité
        start, end = output.find('{'), output.rfind('}') + 1
        if start == -1 or end <= start:
            raise ValueError(f"Réponse LLM sans JSON exploitable : {output[:300]!r}")
        return json.loads(output[start:end])
    finally:
        if os.path.exists(image_path):
            os.unlink(image_path)
