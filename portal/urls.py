from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.root_redirect, name='root'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Stage 2  – auth
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Stage 4  – trucks
    path('trucks/',                 views.truck_list,   name='truck_list'),
    path('trucks/create/',          views.truck_create, name='truck_create'),
    path('trucks/<int:pk>/edit/',   views.truck_edit,   name='truck_edit'),
    path('trucks/<int:pk>/delete/', views.truck_delete, name='truck_delete'),

    # Stage 5  – drivers
    path('drivers/',                 views.driver_list,   name='driver_list'),
    path('drivers/create/',          views.driver_create, name='driver_create'),
    path('drivers/<int:pk>/edit/',   views.driver_edit,   name='driver_edit'),
    path('drivers/<int:pk>/delete/', views.driver_delete, name='driver_delete'),

    # Stage 6  – jobs
    path('jobs/',                    views.job_list,          name='job_list'),
    path('jobs/create/',             views.job_create,        name='job_create'),
    path('jobs/<int:pk>/',           views.job_detail,        name='job_detail'),
    path('jobs/<int:pk>/edit/',      views.job_edit,          name='job_edit'),
    path('jobs/<int:pk>/delete/',    views.job_delete,        name='job_delete'),
    path('jobs/<int:pk>/assign/',    views.job_assign,        name='job_assign'),
    path('jobs/<int:pk>/status/',    views.job_update_status, name='job_update_status'),
    
    # Logs
    path('logs/',                    views.logs_view,         name='logs'),
]
