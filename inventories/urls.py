from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *




# urlpatterns = [


#     path('getuser/', views.GetUserProfile.as_view()), 




# ]


router = DefaultRouter()
router.register(r'filehandling', FilehandlingViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'products', ProductViewSet)
router.register(r'inventory', InventoryLevelViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
