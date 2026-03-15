import { Component, OnInit } from '@angular/core';
import { ClientService } from '../../../services/client/client.service';
import { AsyncPipe, NgForOf } from "@angular/common";
import { Observable } from 'rxjs';
import { User } from '../../../models/models';

@Component({
  selector: 'app-user-card',
  imports: [],
  templateUrl: './user-card.component.html',
  styleUrl: './user-card.component.css'
})
export class UserCardComponent implements OnInit {
  
  users$!: Observable<User[]>;
  constructor(private clientService: ClientService) {}
  ngOnInit() {
    this.users$ = this.clientService.getAllUsers();
  }
}
