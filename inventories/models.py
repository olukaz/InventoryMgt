from django.db import models



class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField()

    def __str__(self):
        return self.name




class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(Supplier, related_name="products", on_delete=models.CASCADE)

    def __str__(self):
        return self.name




class InventoryLevel(models.Model):
    productID = models.OneToOneField(Product, related_name="inventory", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.productID.name} - {self.quantity}"