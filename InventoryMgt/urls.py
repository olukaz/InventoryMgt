
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from drf_yasg import openapi




schema_view = get_schema_view(
   openapi.Info(
      title="Inventory Management System API",
      default_version='v1',
      description="API documentation for the Inventory Management System project.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="support@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('swagger/docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('', include('inventories.urls')),
]


urlpatterns += staticfiles_urlpatterns()







