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
from . import views, compare_views
import debug_toolbar

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("", views.home, name="home"),
    path("compare/", views.compare, name="compare"),
    path("__debug__/", include(debug_toolbar.urls)),
    path("sensors-ids/<int:type_id>/", views.get_sensor_ids, name="sensors_ids"),
    path("sensor-data/<str:sensor_type>/<int:sensor_id>/<str:date>/", views.get_sensor_data, name="sensor_data/"),
    path("compare-days/<str:sensor_type>/<int:sensor_id>/<str:dates>/", views.compare_days, name="compare_days"),
    path("compare-sensors-data/<str:sensor_type1>/<int:sensor_id1>/<str:sensor_type2>/<int:sensor_id2>/<str:date>/", compare_views.compare_sensors_data, name="compare_sensors_data"),
]