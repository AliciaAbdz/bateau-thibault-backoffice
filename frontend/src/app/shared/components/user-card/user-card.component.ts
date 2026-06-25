import { Component, computed } from '@angular/core';
import { AuthService } from '../../../services/auth/auth.service';

@Component({
  selector: 'app-user-card',
  imports: [],
  templateUrl: './user-card.component.html',
  styleUrl: './user-card.component.css'
})
export class UserCardComponent {

  user = computed(() => {
    const jwt = this.authService.currentUser();
    if (!jwt) return null;

    const fullName = (jwt.first_name && jwt.last_name)
      ? `${jwt.first_name} ${jwt.last_name}`
      : jwt.username;

    return {
      name: fullName,
      role: jwt.role,
      lastConnexion: jwt.last_connexion && jwt.last_connexion !== 'None'
        ? new Date(jwt.last_connexion).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
        : 'Première connexion',
      lastModification: jwt.last_modification && jwt.last_modification !== 'None'
        ? new Date(jwt.last_modification).toLocaleDateString('fr-FR')
        : 'N/A'
    };
  });

  constructor(private authService: AuthService) {}
}
