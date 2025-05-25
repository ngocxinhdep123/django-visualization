from django.db import models

class SalesData(models.Model):
    order_id = models.CharField(max_length=100)
    order_date = models.DateField()
    ship_date = models.DateField()
    ship_mode = models.CharField(max_length=50)
    customer_name = models.CharField(max_length=100)
    segment = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    market = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    product_id = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    sub_category = models.CharField(max_length=50)
    product_name = models.CharField(max_length=200)
    sales = models.FloatField()
    quantity = models.IntegerField()
    discount = models.FloatField()
    profit = models.FloatField()
    shipping_cost = models.FloatField()
    order_priority = models.CharField(max_length=50)
    year = models.IntegerField()
    month = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.product_name} - {self.region}"
    