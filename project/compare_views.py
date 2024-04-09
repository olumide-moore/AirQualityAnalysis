from .services.sensor_data_fetcher import SensorDataFetcher
from .services.data_processor import DataProcessor

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from datetime import datetime
import numpy as np

fetcher1= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])
fetcher2= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])

@login_required
def compare_sensors_days(request, sensor_type1, sensor_id1, sensor_type2, sensor_id2, dates):
    """
    Compares the data for two sensors for the given dates.

    :param sensor_type1: str - the type of the first sensor
    :param sensor_id1: int - the id of the first sensor
    :param sensor_type2: str - the type of the second sensor
    :param sensor_id2: int - the id of the second sensor
    :param dates: str - a comma separated string of dates in the format 'YYYY-MM-DD'
    :return: JsonResponse - a json response containing the data for the given dates
    :side effect: updates the cache of the data fetcher
    """
    # ### Test data
    # date='2024-01-22'
    # sensor_type1='Zephyr'
    # sensor_id1 = 60
    # sensor_type2='Zephyr'
    # sensor_id2 = 62
    # dates='2024-01-17,2024-01-18,2024-01-19,2024-01-20,2024-01-21,2024-01-22'
    # ### End test data
    try:
        dates= dates.split(',')
        dates= [datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
    except:
        return JsonResponse(
            {'error': 'Invalid date format'}
        )
    #Check if the two the sensors is linked to fetcher1 or fetcher2 respectively, if not, link them
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
    
    sensors_data=[]
    
    for fetcher in [fetcher1, fetcher2]:
        dates_clone= dates.copy()
        dates_raw_data= {}
        for date in list(fetcher.cacheRawData.keys()):
            if date in dates_clone:
                dates_raw_data[date]= fetcher.cacheRawData[date]
                dates_clone.remove(date)
        if dates_clone:
            rawdata= fetcher.fetch_raw_data(dates_clone)
            dates_raw_data.update(rawdata)
        fetcher.update_cache(dates_raw_data)
        all_dates= sorted(dates_raw_data.keys(), reverse=True)
        all_dates_data= [DataProcessor.convert_df_to_dict(dates_raw_data[date]) for date in all_dates]
        all_dates= [date.strftime('%a, %d-%b') for date in all_dates]
        sensors_data.append({'dates': all_dates, 
                             'no2': [data['no2'] for data in all_dates_data], 
                             'pm2_5': [data['pm2_5'] for data in all_dates_data], 
                             'pm10': [data['pm10'] for data in all_dates_data],
                             'id': fetcher.get_sensor_id()})
    # print(sensors_data)

    
    return JsonResponse(
        {'sensor1': sensors_data[0], 'sensor2': sensors_data[1]}
    )
    

@login_required
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

    correlations= DataProcessor.get_correlations(date_rawdata1, date_rawdata2)

    return JsonResponse(
        {'sensors_info': sensors_info,
            'rawdata': {'sensor1': date_rawdata1_dict, 'sensor2': date_rawdata2_dict},
            'hourly_rawdata': {'sensor1': date_hourly_rawdata1, 'sensor2': date_hourly_rawdata2},
            'correlations': correlations
        }
    )



    