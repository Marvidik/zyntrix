from django.db import models

class InvestmentPlan(models.Model):
    name = models.CharField(max_length=100)  # e.g., Luxury-retirement Plan
    price = models.BigIntegerField()  # e.g., 15000000
    duration = models.PositiveIntegerField()  # e.g., 10

    profit_percent = models.FloatField()  # e.g., 7.9

    min_deposit = models.BigIntegerField()
    max_deposit = models.BigIntegerField()

    min_return_percent = models.FloatField(default=0.0)
    max_return_percent = models.FloatField()

    bonus = models.BigIntegerField(default=0)  # Optional bonus amount

    def __str__(self):
        return self.name
    

class PaymentMethods(models.Model):
    name=models.CharField(max_length=100)
    network=models.CharField(max_length=100)
    address=models.CharField(max_length=100)


class Settings(models.Model):
    kyc=models.BooleanField(default=False)
    verification=models.BooleanField(default=False)