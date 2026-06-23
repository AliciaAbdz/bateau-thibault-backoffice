import { Component, OnInit } from '@angular/core';
import { ClientService } from '../../../services/client/client.service';
import { AsyncPipe, NgForOf } from "@angular/common";
import { Observable, of } from 'rxjs';
import { User } from '../../../models/models';
import { AuthService } from '../../../services/auth/auth.service';

@Component({
  selector: 'app-team-card',
  imports: [NgForOf, AsyncPipe],
  templateUrl: './team-card.component.html',
  styleUrl: './team-card.component.css'
})
export class TeamCardComponent implements OnInit {

  members$!: Observable<User[]>;

  constructor(
    private clientService: ClientService,
    private authService: AuthService
  ) {}

  ngOnInit() {
    const retailerId = this.authService.getRetailerId();
    if (retailerId) {
      this.members$ = this.clientService.getTeamMembers(retailerId);
    } else {
      this.members$ = of([]);
    }
  }
}
