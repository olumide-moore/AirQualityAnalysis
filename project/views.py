from django.shortcuts import render
from .models import *
from .services import *
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
from django.views import View
import pandas as pd
import numpy as np
from django.db.utils import DatabaseError
import time

# data_table= AllSensorMeasurementsWithLocationsZephyr
# data_table= AllSensorMeasurementsWithLocationsSc
# data_table= AllPlumeMeasurements
#49, 47,29, 11
data_fetcher= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])
aqi_obj = AQI()

def home(request):
    sensorType1= request.GET.get('sensorType1')
    sensorId1= request.GET.get('sensorId1')
    date= request.GET.get('date')
    sensor_types= get_sensor_types()
    return render(request, 'home.html',
                  context={'sensor_types': sensor_types,
                            'sensorType1': sensorType1,
                            'sensorId1': sensorId1,
                            'date': date}
                           )

def compare(request):
    sensorType1= request.GET.get('sensorType1')
    sensorId1= request.GET.get('sensorId1')
    date= request.GET.get('date')
    sensor_types= get_sensor_types()
    return render(request, 'compare.html',
                context={'sensor_types': sensor_types,
                         'sensorType1': sensorType1,
                            'sensorId1': sensorId1,
                            'date': date})
def get_sensor_types():
    sensor_types  = Sensortypes.objects.values('id','name').distinct()
    sensor_types = dict(map(lambda x: (x['id'], x['name']),sensor_types))
    return sensor_types

def get_sensor_ids(request, type_id):
    start = time.time()
    # sensors = Sensors.objects.values('id', 'lookup_id', 'active', 'time_created', 'stationary_box', 'user_id').filter(type_id=type_id)
    sensors = Sensors.objects.values('id').filter(type_id=type_id)
    sensorsids=list(map(lambda x: x['id'], sensors))
    print('Time taken: ', (time.time()-start) * 1000, 'ms')
    
    return JsonResponse(
        {'sensors': sensorsids}
    )

def compare_days(request, sensor_type, sensor_id, dates):
    """
    Fetches the raw data from the database for the given sensor_id and the required concentrations for the given dates.
    If the data is not available in the cache, it fetches the data from the database and updates the cache.

    :param sensor_type: str - the type of the sensor
    :param sensor_id: int - the id of the sensor
    :param dates: str - a comma separated string of dates in the format 'YYYY-MM-DD'
    :return: JsonResponse - a json response containing the data for the given dates
    :side effect: updates the cache with the fetched data

    """
    try:
        dates = dates.split(',')
        dates = [datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
    except:
        return JsonResponse(
            {'error': 'Invalid date format'}
        )
    if 'data_fetcher' not in globals():
        global data_fetcher
        data_fetcher= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])
    
    if data_fetcher.getSensorType() != sensor_type:
        data_fetcher.setSensorType(sensor_type)
        data_fetcher.setSensorId(sensor_id)
    if data_fetcher.getSensorId() != sensor_id:
        data_fetcher.setSensorId(sensor_id)
    
    dates_hourly_data={}
    #Check if the data for the given dates is available in the cache
    for date in list(data_fetcher.cacheHourlyAvgs.keys()):
        if date in dates:
            dates_hourly_data[date]= data_fetcher.cacheHourlyAvgs[date]
            # print(dates_hourly_data[date])
            dates.remove(date)
    if dates: #If the data for some dates is not available in the cache, fetch the data from the database
        dates_raw_data = data_fetcher.getRawData(dates)
        for date, data in dates_raw_data.items():
            hourly_avgs = data_fetcher.getHourlyAverages(data, date)
            dates_hourly_data[date]= hourly_avgs
        #update the cache
        data_fetcher.updateCache(dates_raw_data, dates_hourly_data)
    #sort the data by date
    sorted_dates= sorted(dates_hourly_data.keys(), reverse=True)

    # dates_hourly_data = {key.strftime('%a, %d-%b'): value for key, value in dates_hourly_data.items()}
    dates_hourly_data = {key.strftime('%a, %d-%b'): dates_hourly_data[key] for key in sorted_dates}
    # print(dates_hourly_data.keys())
    return JsonResponse(
        {'data': dates_hourly_data}
    )


def get_sensor_data(request, sensor_type, sensor_id, date):
    """
    Fetches the raw data from the database for the given sensor_id and the required concentrations for the given date.
    If the data is not available in the cache, it fetches the data from the database and updates the cache.
    :param sensor_type: str - the type of the sensor
    :param sensor_id: int - the id of the sensor
    :param date: str - the date in the format 'YYYY-MM-DD'
    :return: JsonResponse - a json response containing the data for the given date - last updated date, rawdata, hourly averages, hourly aqis, average data, aqi data
    :side effect: updates the cache with the fetched data
    """
    try:
        ### Test data
        # date='2024-01-22'
        # sensor_type='Zephyr'
        # sensor_id = 60
        ### End test data
        date = datetime.strptime(date, '%Y-%m-%d').date()
    except:
        return JsonResponse(
            {'error': 'Invalid date format'}
        )
    #Check if data_fetcher exists in the global scope
    if 'data_fetcher' not in globals():
        global data_fetcher
        data_fetcher= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])

    #Check if sensor_type is changed
    if data_fetcher.getSensorType() != sensor_type:
        data_fetcher.setSensorType(sensor_type)
        data_fetcher.setSensorId(sensor_id) #If sensor_type is changed, also change the sensor_id
    #Check if sensor_id is changed
    if data_fetcher.getSensorId() != sensor_id:
        data_fetcher.setSensorId(sensor_id)

    last_updated = data_fetcher.getLastUpdatedTime()

    if date != date.today() and date in data_fetcher.cacheRawData:
        rawdata = data_fetcher.cacheRawData[date]
        hourly_avgs = data_fetcher.cacheHourlyAvgs[date]
        # print(data_fetcher.cacheRawData.keys())
    else:
        rawdata = data_fetcher.getRawData([date]).get(date)
        hourly_avgs = data_fetcher.getHourlyAverages(rawdata, date)
        data_fetcher.updateCache({date: rawdata}, {date: hourly_avgs})

    hourly_aqis = aqi_obj.compute_hourly_aqis(hourly_avgs)

    no2_hourly_avgs= data_fetcher.getNO2_HourlyAvgs(rawdata['no2'], minute_threshold= 45)
    no2_hourly_avg_max = no2_hourly_avgs.max()
    if no2_hourly_avg_max in [np.nan, None]:   no2_hourly_avg_max = None
    pm2_5_24houravg = data_fetcher.getPM2_5_24HourAvg(rawdata['pm2_5'],minute_threshold= 1080)
    pm10_24houravg = data_fetcher.getPM10_24HourAvg(rawdata['pm10'],minute_threshold= 1080)

    no2_hourly_avg_max = round(no2_hourly_avg_max, 2) if no2_hourly_avg_max else None
    pm2_5_24houravg = round(pm2_5_24houravg, 2) if pm2_5_24houravg else None
    pm10_24houravg = round(pm10_24houravg, 2) if pm10_24houravg else None
    avg_data = {'no2': no2_hourly_avg_max, 'pm2_5': pm2_5_24houravg, 'pm10': pm10_24houravg}
    aqi_data = {'no2': aqi_obj.getNO2Index(no2_hourly_avg_max), 'pm2_5': aqi_obj.getPM2_5Index(pm2_5_24houravg), 'pm10': aqi_obj.getPM10Index(pm10_24houravg)}

    rawdata_dict = data_fetcher.convert_df_to_dict(rawdata)
    return JsonResponse(
        {'last_updated': last_updated, 
        'rawdata': rawdata_dict,
        'hourly_avgs':hourly_avgs, 
        'hourly_aqis':hourly_aqis,
        'avg_data': avg_data,
        'aqi_data': aqi_data
        }
    )
    