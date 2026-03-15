import { Injectable } from '@angular/core';
import { ClientService } from '../client/client.service';
import { User } from '../../models/models';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private clientService : ClientService) { }

}
