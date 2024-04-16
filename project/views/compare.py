from ..services.sensor_data_fetcher import SensorDataFetcher
from ..services.data_processor import DataProcessor
from ..services import sensors_metadata

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from datetime import datetime
import numpy as np

fetcher1= SensorDataFetcher()
fetcher2= SensorDataFetcher()

@login_required
def initialize_page(request):
    sensorType1= request.POST.get('sensorType1')
    sensorId1= request.POST.get('sensorId1')
    date= request.POST.get('dateInput')
    sensor_types= sensors_metadata.get_all_sensor_types()
    return render(request, 'compare.html',
                context={'sensor_types': sensor_types,
                         'sensorType1': sensorType1,
                            'sensorId1': sensorId1,
                            'date': date})

@login_required
def correlationguide(request):
    return render(request, 'correlationguide.html')


@login_required
def get_data_for_date(request, sensor_type1, sensor_id1, sensor_type2, sensor_id2, date, corravginterval):
    """
    Compares the data for two sensors for the given date.

    :param sensor_type1: str - the type of the first sensor
    :param sensor_id1: int - the id of the first sensor
    :param sensor_type2: str - the type of the second sensor
    :param sensor_id2: int - the id of the second sensor
    :param date: str - the date in the format 'YYYY-MM-DD'
    :param corravginterval: int - the interval for calculating the correlation
    :return: JsonResponse - a json response containing the data for the given date
    """
    # ### Test data
    # date='2024-01-22'
    # sensor_type1='Zephyr'
    # sensor_id1 = 60
    # sensor_type2='Zephyr'
    # sensor_id2 = 62
    # ### End test data
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    except:
        return JsonResponse(
            {'error': 'Invalid date format'}
        )
 
    #Check if the two the sensors is linked to fetcher1 or fetcher2, if not, link them
    if fetcher1.get_sensor_type() != sensor_type1:
        fetcher1.set_sensor_type(sensor_type1)
        fetcher1.set_sensor_id(sensor_id1)
    if fetcher1.get_sensor_id() != sensor_id1:
        print('setting sensor id')
        fetcher1.set_sensor_id(sensor_id1)
        print(fetcher1.get_sensor_id())
        
    if fetcher2.get_sensor_type() != sensor_type2:
        fetcher2.set_sensor_type(sensor_type2)
        fetcher2.set_sensor_id(sensor_id2)
    if fetcher2.get_sensor_id() != sensor_id2:
        fetcher2.set_sensor_id(sensor_id2)

    if date!=date.today() and date in fetcher1.cacheRawData:
        date_rawdata1= fetcher1.cacheRawData[date]
    else:
        date_rawdata1 = fetcher1.fetch_raw_data([date]).get(date)
        fetcher1.update_cache({date: date_rawdata1})
    if date!=date.today() and date in fetcher2.cacheRawData:
        date_rawdata2= fetcher2.cacheRawData[date]
    else:
        date_rawdata2 = fetcher2.fetch_raw_data([date]).get(date)
        fetcher2.update_cache({date: date_rawdata2})

    date_hourly_rawdata1= DataProcessor.extract_hrly_raw_data(date_rawdata1)
    date_hourly_rawdata2= DataProcessor.extract_hrly_raw_data(date_rawdata2)
    
    sensors_info= {'sensor1': {'type': fetcher1.get_sensor_type(), 'id': fetcher1.get_sensor_id(), 'last_updated': fetcher1.fetch_last_updated()},
                     'sensor2': {'type': fetcher2.get_sensor_type(), 'id': fetcher2.get_sensor_id(), 'last_updated': fetcher2.fetch_last_updated()}
                     }
    date_rawdata1_dict= DataProcessor.convert_df_to_dict(date_rawdata1)
    date_rawdata2_dict= DataProcessor.convert_df_to_dict(date_rawdata2)
    date_rawdata1_dict['id']= fetcher1.get_sensor_id()
    date_rawdata2_dict['id']= fetcher2.get_sensor_id()
    date_hourly_rawdata1['id']= fetcher1.get_sensor_id()
    date_hourly_rawdata2['id']= fetcher2.get_sensor_id()

    correlations= DataProcessor.get_correlations(date_rawdata1, date_rawdata2, corravginterval=corravginterval)

    return JsonResponse(
        {'sensors_info': sensors_info,
            'rawdata': {'sensor1': date_rawdata1_dict, 'sensor2': date_rawdata2_dict},
            'hourly_rawdata': {'sensor1': date_hourly_rawdata1, 'sensor2': date_hourly_rawdata2},
            'correlations': correlations
        }
    )


def updateCorrelation(request, sensor_type1, sensor_id1, sensor_type2, sensor_id2, date, corravginterval):
    """
    Updates the correlation between the data for two sensors for the given date.

    :param sensor_type1: str - the type of the first sensor
    :param sensor_id1: int - the id of the first sensor
    :param sensor_type2: str - the type of the second sensor
    :param sensor_id2: int - the id of the second sensor
    :param date: str - the date in the format 'YYYY-MM-DD'
    :param corravginterval: int - the resolution to aggregate the data to
    :return: JsonResponse - a json response containing the updated correlations for the given date
    """
    # ### Test data
    # date='2024-01-20'
    # sensor_type1='Zephyr'
    # sensor_id1 = 60
    # sensor_type2='Zephyr'
    # sensor_id2 = 62
    # ### End test data
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    except:
        return JsonResponse(
            {'error': 'Invalid date format'}
        )
    #Check if the two the sensors is linked to fetcher1 or fetcher2, if not, link them
    if fetcher1.get_sensor_type() != sensor_type1:
        fetcher1.set_sensor_type(sensor_type1)
        fetcher1.set_sensor_id(sensor_id1)
    if fetcher1.get_sensor_id() != sensor_id1:
        fetcher1.set_sensor_id(sensor_id1)
        
    if fetcher2.get_sensor_type() != sensor_type2:
        fetcher2.set_sensor_type(sensor_type2)
        fetcher2.set_sensor_id(sensor_id2)
    if fetcher2.get_sensor_id() != sensor_id2:
        fetcher2.set_sensor_id(sensor_id2)

    if date!=date.today() and date in fetcher1.cacheRawData:
        date_rawdata1= fetcher1.cacheRawData[date]
    else:
        date_rawdata1 = fetcher1.fetch_raw_data([date]).get(date)
        fetcher1.update_cache({date: date_rawdata1})
    if date!=date.today() and date in fetcher2.cacheRawData:
        date_rawdata2= fetcher2.cacheRawData[date]
    else:
        date_rawdata2 = fetcher2.fetch_raw_data([date]).get(date)
        fetcher2.update_cache({date: date_rawdata2})
    correlations= DataProcessor.get_correlations(date_rawdata1, date_rawdata2, corravginterval=corravginterval)

    return JsonResponse(
        {'correlations': correlations}
    )
    
