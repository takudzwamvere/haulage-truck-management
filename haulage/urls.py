from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from core.api import truck_router, driver_router, job_router, auth_router
from core.auth import AuthBearer

auth = AuthBearer()

api = NinjaAPI(title='Haulage Truck Management API', version='1.0.0')

api.add_router('/auth/', auth_router)
api.add_router('/trucks/', truck_router, auth=auth)
api.add_router('/drivers/', driver_router, auth=auth)
api.add_router('/jobs/', job_router, auth=auth)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]