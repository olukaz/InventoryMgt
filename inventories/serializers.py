from .models import *
from rest_framework import serializers



class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'



class ProductSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(), source="supplier", write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'supplier', 'supplier_id']



class InventoryLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLevel
        fields = ['id', 'productID', 'quantity']
