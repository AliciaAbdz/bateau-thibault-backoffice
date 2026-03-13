import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

/**
 * Interface pour les données utilisateur affichées dans le header
 */
export interface UserHeaderData {
  name: string;
  role: string;
  avatarUrl?: string;
}
 
/**
 * Composant Header de l'application
 * 
 * Affiche :
 * - Le logo de l'application
 * - Les informations de l'utilisateur connecté
 * - Un bouton de déconnexion
 * 
 * @example
 * <mobile-header 
 *   [user]="currentUser" 
 *   (logout)="handleLogout()">
 * </mobile-header>
 */

@Component({
  selector: 'mobile-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './mobile-header.component.html',
  styleUrls: ['./mobile-header.component.css']
})
export class MobileHeaderComponent {
  /**
   * Données de l'utilisateur connecté à afficher dans le header
   */
 
  private default_user : UserHeaderData = {
  name : "Sivan Cozzo",
  role : "admin",
  }

  @Input() user: UserHeaderData | UserHeaderData = this.default_user;

  /**
   * Afficher ou masquer le menu utilisateur au clic
   */
  @Input() showUserMenu = true;
 
  /**
   * Afficher ou masquer le menu utilisateur au clic
   */
  @Input() StepName = "ADD ITEM";

  /**
   * Événement émis lors du clic sur le bouton de déconnexion
   */
  @Output() logout = new EventEmitter<void>();
 
  /**
   * État du menu dropdown utilisateur (ouvert/fermé)
   */
  isUserMenuOpen = false;
 
  constructor(private router: Router) {}
 
  /**
   * Gère le clic sur le bouton de déconnexion
   */
  onLogout(): void {
    this.isUserMenuOpen = false;
    this.logout.emit();
  }
 
  /**
   * Toggle le menu dropdown utilisateur
   */
  toggleUserMenu(): void {
    this.isUserMenuOpen = !this.isUserMenuOpen;
  }
 
  /**
   * Ferme le menu utilisateur
   */
  closeUserMenu(): void {
    this.isUserMenuOpen = false;
  }
 
  /**
   * Navigation vers le profil utilisateur
   */
  navigateToProfile(): void {
    this.closeUserMenu();
    this.router.navigate(['/profile']);
  }
 
 
  /**
   * Retourne les initiales de l'utilisateur pour l'avatar par défaut
   */
  getUserInitials(): string {
    if (!this.user?.name) return '';
    
    const names = this.user.name.split(' ');
    if (names.length >= 2) {
      return `${names[0][0]}${names[1][0]}`.toUpperCase();
    }
    return this.user.name.substring(0, 2).toUpperCase();
  }
}