import os
import csv
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.conf import settings
from .models import Supplier, Product, InventoryLevel


class SupplierViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.supplier_data = {"name": "Test Supplier", "contact_info": "123 Test Street"}
        self.supplier = Supplier.objects.create(**self.supplier_data)

    def test_create_supplier(self):
        response = self.client.post("/suppliers/", self.supplier_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 2)

    def test_list_suppliers(self):
        response = self.client.get("/suppliers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_supplier(self):
        updated_data = {"name": "Updated Supplier", "contact_info": "456 Updated Street"}
        response = self.client.put(f"/suppliers/{self.supplier.id}/", updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.supplier.refresh_from_db()
        self.assertEqual(self.supplier.name, "Updated Supplier")

    def test_delete_supplier(self):
        response = self.client.delete(f"/suppliers/{self.supplier.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Supplier.objects.count(), 0)


class ProductViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.supplier = Supplier.objects.create(name="Test Supplier", contact_info="123 Test Street")
        self.product_data = {
            "name": "Test Product",
            "description": "A test product",
            "price": "99.99",
            "supplier": self.supplier.id,
        }
        self.product = Product.objects.create(**self.product_data)

    def test_create_product(self):
        response = self.client.post("/products/", self.product_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_list_products(self):
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_product(self):
        updated_data = {
            "name": "Updated Product",
            "description": "An updated test product",
            "price": "89.99",
            "supplier": self.supplier.id,
        }
        response = self.client.put(f"/products/{self.product.id}/", updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product")

    def test_delete_product(self):
        response = self.client.delete(f"/products/{self.product.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_upload_csv(self):
        # Create a CSV file
        csv_file_path = os.path.join(settings.BASE_DIR, "test_products.csv")
        with open(csv_file_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["name", "description", "price", "supplier_id"])
            writer.writeheader()
            writer.writerow({"name": "CSV Product", "description": "From CSV", "price": "49.99", "supplier_id": self.supplier.id})

        with open(csv_file_path, "rb") as file:
            response = self.client.post("/products/upload-csv/", {"file": file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 2)

        # Clean up test CSV file
        os.remove(csv_file_path)


class InventoryLevelViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.supplier = Supplier.objects.create(name="Test Supplier", contact_info="123 Test Street")
        self.product = Product.objects.create(name="Test Product", description="A test product", price="99.99", supplier=self.supplier)
        self.inventory_data = {"productID": self.product.id, "quantity": 20}
        self.inventory = InventoryLevel.objects.create(**self.inventory_data)

    def test_create_inventory(self):
        new_inventory_data = {"productID": self.product.id, "quantity": 15}
        response = self.client.post("/inventorylevels/", new_inventory_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InventoryLevel.objects.count(), 2)

    def test_list_inventory_levels(self):
        response = self.client.get("/inventorylevels/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_inventory(self):
        updated_data = {"productID": self.product.id, "quantity": 50}
        response = self.client.put(f"/inventorylevels/{self.inventory.id}/", updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 50)

    def test_delete_inventory(self):
        response = self.client.delete(f"/inventorylevels/{self.inventory.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(InventoryLevel.objects.count(), 0)

    def test_generate_report(self):
        response = self.client.get("/products/generate-report/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Report generated successfully", response.data["message"])
