from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from ninja.security import django_auth
from core.api import truck_router, driver_router, job_router

api = NinjaAPI(title='Haulage Truck Management API', version='1.0.0')

api.add_router('/trucks/', truck_router, auth=django_auth)
api.add_router('/drivers/', driver_router, auth=django_auth)
api.add_router('/jobs/', job_router, auth=django_auth)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]