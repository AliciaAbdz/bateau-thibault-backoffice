import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ValidateProductPageComponent } from './validate-product-page.component';

describe('ValidateProductPageComponent', () => {
  let component: ValidateProductPageComponent;
  let fixture: ComponentFixture<ValidateProductPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ValidateProductPageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ValidateProductPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
