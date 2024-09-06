# from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.homepage, name='home'),
    # path('all-projects/', views.all_projects, name='all_projects'),
]
