import os
import csv
from django.conf import settings
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from io import TextIOWrapper
from rest_framework.parsers import MultiPartParser
from django.utils.timezone import now



class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price']




class ProductMultiViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser]  # Allow file upload

    @action(detail=False, methods=['post'], url_path='upload-csv')
    def upload_csv(self, request):
        """
        Upload and process a CSV file containing product data.
        """
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            csv_file = TextIOWrapper(file.file, encoding='utf-8')
            reader = csv.DictReader(csv_file)

            required_fields = ['name', 'description', 'price', 'supplier_id']
            errors = []
            processed_count = 0

            for row_number, row in enumerate(reader, start=1):
                # Check for required fields
                if not all(field in row for field in required_fields):
                    errors.append(f"Row {row_number}: Missing required fields.")
                    continue

                # Validate price
                try:
                    row['price'] = float(row['price'])
                except ValueError:
                    errors.append(f"Row {row_number}: Invalid price format.")
                    continue

                # Check if supplier exists
                supplier_id = row.get('supplier_id')
                try:
                    supplier = Supplier.objects.get(id=supplier_id)
                except Supplier.DoesNotExist:
                    errors.append(f"Row {row_number}: Supplier with ID {supplier_id} does not exist.")
                    continue

                # Save product
                product_data = {
                    'name': row['name'],
                    'description': row['description'],
                    'price': row['price'],
                    'supplier': supplier,
                }
                Product.objects.create(**product_data)
                processed_count += 1

            return Response({
                "processed_count": processed_count,
                "errors": errors,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='generate-report')
    def generate_report(self, request):
        """
        Generate a report on inventory levels and low stock alerts.
        """
        report_data = []
        low_stock_threshold = 10

        # Fetch data
        inventory_levels = InventoryLevel.objects.select_related('productID')
        for inventory in inventory_levels:
            product = inventory.productID
            report_data.append({
                'product_name': product.name,
                'quantity': inventory.quantity,
                'low_stock_alert': inventory.quantity < low_stock_threshold,
                'supplier': product.supplier.name,
            })

        # Save the report
        timestamp = now().strftime("%Y%m%d_%H%M%S")
        downloads_folder = os.path.join(settings.BASE_DIR, 'downloads')
        os.makedirs(downloads_folder, exist_ok=True)  # Ensure the folder exists
        report_file = os.path.join(downloads_folder, f"inventory_report_{timestamp}.csv")
        with open(report_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['product_name', 'quantity', 'low_stock_alert', 'supplier'])
            writer.writeheader()
            writer.writerows(report_data)

        return Response({"message": f"Report generated successfully: {report_file}"}, status=status.HTTP_200_OK)


       
    



class InventoryLevelViewSet(viewsets.ModelViewSet):
    queryset = InventoryLevel.objects.all()
    serializer_class = InventoryLevelSerializer

    def create(self, request, *args, **kwargs):
        # Simplify creation by directly using validated data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()