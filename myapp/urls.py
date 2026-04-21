from django.urls import path
from . import views

app_name = 'myapp'

# add the necessary urls here for app to run

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),

    # Pokemon CRUD
    path('pokemon/', views.record_list, name='record_list'),
    path('pokemon/<int:pk>/', views.record_detail, name='record_detail'),
    path('pokemon/add/', views.record_create, name='record_create'),
    path('pokemon/<int:pk>/edit/', views.record_update, name='record_update'),
    path('pokemon/<int:pk>/delete/', views.record_delete, name='record_delete'),

    # Analytics dashboard uncomment when analytics dashboard is made
    # path('analytics/', views.analytics, name='analytics'),

    # API fetch trigger (staff only)
    path('fetch/', views.fetch_page, name='fetch'),
    path('fetch/run/', views.fetch_data_view, name='fetch_run'),
]