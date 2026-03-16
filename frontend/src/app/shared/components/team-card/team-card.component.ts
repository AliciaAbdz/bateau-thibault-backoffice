import { Component, OnInit } from '@angular/core';
import { ClientService } from '../../../services/client/client.service';
import { AsyncPipe, NgForOf } from "@angular/common";
import { Observable } from 'rxjs';
import { User } from '../../../models/models';
@Component({
  selector: 'app-team-card',
  imports: [NgForOf, AsyncPipe],
  templateUrl: './team-card.component.html',
  styleUrl: './team-card.component.css'
})
export class TeamCardComponent implements OnInit {
  
  members$!: Observable<User[]>;
  constructor(private clientService: ClientService) {}
  ngOnInit() {
    const userId = 1
    this.members$ = this.clientService.getTeamMembers(userId);
  }
}
