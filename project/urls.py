"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import compare, home
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home.initialize_page, name="home"),
    path("", include("authentication.urls")),
    path("home/", home.initialize_page, name="home"),
    path("compare/", compare.initialize_page, name="compare"),
    path("aqiguide/", home.aqiguide, name="aqiguide"),
    path("__debug__/", include(debug_toolbar.urls)),
    path("sensors-ids/<int:type_id>/", home.get_sensor_ids, name="sensors_ids"),
    path("sensor/<str:sensor_type>/<int:sensor_id>/date/<str:date>/", home.get_data_for_date, name="sensor_data_for_date"),
    path("sensor/<str:sensor_type>/<int:sensor_id>/dates/<str:dates>/", home.get_data_across_dates, name="sensor_compare_days"),
    path("sensors/compare/<str:sensor_type1>/<int:sensor_id1>/and/<str:sensor_type2>/<int:sensor_id2>/date/<str:date>/", compare.get_data_for_date, name="sensors_data_for_date"),
    path("sensors/compare/<str:sensor_type1>/<int:sensor_id1>/and/<str:sensor_type2>/<int:sensor_id2>/dates/<str:dates>/", compare.get_data_across_dates, name="sensors_data_across_dates"),
]