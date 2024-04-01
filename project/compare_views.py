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


data_fetcher1= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])
data_fetcher2= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])

def compare_sensors_data(request, sensor_type1, sensor_id1, sensor_type2, sensor_id2, date):
    """
    Compares the data for two sensors for the given date.

    :param sensor_type1: str - the type of the first sensor
    :param sensor_id1: int - the id of the first sensor
    :param sensor_type2: str - the type of the second sensor
    :param sensor_id2: int - the id of the second sensor
    :param date: str - the date in the format 'YYYY-MM-DD'
    :return: JsonResponse - a json response containing the data for the given date
    """
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    except:
        return JsonResponse(
            {'error': 'Invalid date format'}
        )
    if 'data_fetcher1' not in globals():
        global data_fetcher1
        data_fetcher1= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])
    if 'data_fetcher2' not in globals():
        global data_fetcher2
        data_fetcher2= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])

    #Check if the two the sensors is linked to data_fetcher1 or data_fetcher2, if not, link them
    if data_fetcher1.getSensorType() != sensor_type1:
        data_fetcher1.setSensorType(sensor_type1)
        data_fetcher1.setSensorId(sensor_id1)
    if data_fetcher1.getSensorId() != sensor_id1:
        data_fetcher1.setSensorId(sensor_id1)
        
    if data_fetcher2.getSensorType() != sensor_type2:
        data_fetcher2.setSensorType(sensor_type2)
        data_fetcher2.setSensorId(sensor_id2)
    if data_fetcher2.getSensorId() != sensor_id2:
        data_fetcher2.setSensorId(sensor_id2)

    if date!=date.today() and date in data_fetcher1.cacheRawData:
            rawdata1= data_fetcher1.cacheRawData[date]
    else:
        rawdata1 = data_fetcher1.getRawData([date]).get(date)
        data_fetcher1.updateCache({date: rawdata1})
    if date!=date.today() and date in data_fetcher2.cacheRawData:
        rawdata2= data_fetcher2.cacheRawData[date]
    else:
        rawdata2 = data_fetcher2.getRawData([date]).get(date)
        data_fetcher2.updateCache({date: rawdata2})
    
    sensors_info= {'sensor1': {'type': data_fetcher1.getSensorType(), 'id': data_fetcher1.getSensorId(), 'last_updated': data_fetcher1.getLastUpdatedTime()},
                     'sensor2': {'type': data_fetcher2.getSensorType(), 'id': data_fetcher2.getSensorId(), 'last_updated': data_fetcher2.getLastUpdatedTime()}
                     }
    mintuely_avgs1 = data_fetcher1.getMinutelyAverages(rawdata1, date)
    mintuely_avgs1['id'] = data_fetcher1.getSensorId()
    mintuely_avgs2 = data_fetcher2.getMinutelyAverages(rawdata2, date)
    mintuely_avgs2['id'] = data_fetcher2.getSensorId()

    return JsonResponse(
        {'sensors_info': sensors_info,
            'minutely_avgs': {'sensor1': mintuely_avgs1, 'sensor2': mintuely_avgs2}}
    )