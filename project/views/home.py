from ..services.sensor_data_fetcher import SensorDataFetcher
from ..services.data_processor import DataProcessor
from ..services.aqi_calculator import AQICalculator
from ..services import sensors_metadata

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from datetime import datetime
import numpy as np

# import time

fetcher= SensorDataFetcher()

@login_required
def initialize_page(request):
    sensor_types= sensors_metadata.get_all_sensor_types()
    return render(request, 'home.html',
                  context={'sensor_types': sensor_types}
                  )

@login_required
def get_sensor_ids(request, type_id):
    sensorsids= sensors_metadata.get_sensor_ids(type_id)    
    return JsonResponse(
        {'sensors': sensorsids}
    )
@login_required
def aqiguide(request):
    return render(request, 'aqiguide.html')

@login_required
def howto(request):
    return render(request, 'howto.html')

@login_required
def get_data_for_date(request, sensor_type, sensor_id, date):
    """
    Fetches the raw data from the database for the given sensor_id and the required concentrations for the given date.
    If the data is not available in the cache, it fetches the data from the database and updates the cache.
    :param sensor_type: str - the type of the sensor
    :param sensor_id: int - the id of the sensor
    :param date: str - the date in the format 'YYYY-MM-DD'
    :return: JsonResponse - a json response containing the data for the given date - last updated date, rawdata, hourly averages, hourly aqis, average data, aqi data
    :side effect: updates the cache with the fetched data
    """
    # # Test data
    # date='2024-01-22'
    # sensor_type='Zephyr'
    # sensor_id = 60
    # ## End test data
    try:        
        date = datetime.strptime(date, '%Y-%m-%d').date()
    except:
        return JsonResponse(
            {'error': 'Invalid date format'}
        )

    #Check if sensor_type is changed
    if fetcher.get_sensor_type() != sensor_type:
        fetcher.set_sensor_type(sensor_type)
        fetcher.set_sensor_id(sensor_id) #If sensor_type is changed, also change the sensor_id
    #Check if sensor_id is changed
    if fetcher.get_sensor_id() != sensor_id:
        fetcher.set_sensor_id(sensor_id)

    last_updated = fetcher.fetch_last_updated()

    if date != date.today() and date in fetcher.cacheRawData:
        rawdata = fetcher.cacheRawData[date]
        hourly_avgs = fetcher.cacheHourlyAvgs[date]
        # print(fetcher.cacheRawData.keys())
    else:
        rawdata = fetcher.fetch_raw_data([date]).get(date)
        hourly_avgs = DataProcessor.calc_hrly_avgs_pollutants(rawdata, date)
        fetcher.update_cache({date: rawdata}, {date: hourly_avgs})

    hourly_aqis = AQICalculator.compute_hourly_aqis(hourly_avgs)

    no2_hourly_avgs= DataProcessor.calc_hrly_avgs_single_pollutant(rawdata['no2'], minute_threshold= 45)
    no2_hourly_avg_max = no2_hourly_avgs.max()
    if no2_hourly_avg_max in [np.nan, None]:   no2_hourly_avg_max = None
    pm2_5_24houravg = DataProcessor.calc_24hr_avg_single_pollutant(rawdata['pm2_5'],minute_threshold= 1080)
    pm10_24houravg = DataProcessor.calc_24hr_avg_single_pollutant(rawdata['pm10'],minute_threshold= 1080)

    no2_hourly_avg_max = round(no2_hourly_avg_max, 2) if no2_hourly_avg_max else None
    pm2_5_24houravg = round(pm2_5_24houravg, 2) if pm2_5_24houravg else None
    pm10_24houravg = round(pm10_24houravg, 2) if pm10_24houravg else None
    avg_data = {'no2': no2_hourly_avg_max, 'pm2_5': pm2_5_24houravg, 'pm10': pm10_24houravg}
    aqi_data = {'no2': AQICalculator.get_no2_index(no2_hourly_avg_max), 'pm2_5': AQICalculator.get_pm2_5_index(pm2_5_24houravg), 'pm10': AQICalculator.get_pm10_index(pm10_24houravg)}

    rawdata_dict = DataProcessor.convert_df_to_dict(rawdata)
    return JsonResponse(
        {'last_updated': last_updated, 
        'rawdata': rawdata_dict,
        'hourly_avgs':hourly_avgs, 
        'hourly_aqis':hourly_aqis,
        'avg_data': avg_data,
        'aqi_data': aqi_data
        }
    )
    

@login_required
def get_data_across_dates(request, sensor_type, sensor_id, dates):
    """
    Fetches the raw data from the database for the given sensor_id and the required concentrations for the given dates.
    If the data is not available in the cache, it fetches the data from the database and updates the cache.

    :param sensor_type: str - the type of the sensor
    :param sensor_id: int - the id of the sensor
    :param dates: str - a comma separated string of dates in the format 'YYYY-MM-DD'
    :return: JsonResponse - a json response containing the data for the given dates
    :side effect: updates the cache with the fetched data

    """
    # ## Test data
    # date='2024-01-22'
    # sensor_type='Zephyr'
    # sensor_id = 60
    # dates='2024-01-17,2024-01-18,2024-01-19,2024-01-20,2024-01-21,2024-01-22'
    # ## End test data
    try:
        dates = dates.split(',')
        dates = [datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
    except:
        return JsonResponse(
            {'error': 'Invalid date format'}
        )
    if fetcher.get_sensor_type() != sensor_type:
        fetcher.set_sensor_type(sensor_type)
        fetcher.set_sensor_id(sensor_id)
    if fetcher.get_sensor_id() != sensor_id:
        fetcher.set_sensor_id(sensor_id)
    
    dates_hourly_data={}
    #Check if the data for the given dates is available in the cache
    for date in list(fetcher.cacheHourlyAvgs.keys()):
        if date in dates:
            dates_hourly_data[date]= fetcher.cacheHourlyAvgs[date]
            # print(dates_hourly_data[date])
            dates.remove(date)
    if dates: #If the data for some dates is not available in the cache, fetch the data from the database
        dates_raw_data = fetcher.fetch_raw_data(dates)
        for date, data in dates_raw_data.items():
            hourly_avgs = DataProcessor.calc_hrly_avgs_pollutants(data, date)
            dates_hourly_data[date]= hourly_avgs
        #update the cache
        fetcher.update_cache(dates_raw_data, dates_hourly_data)
    #sort the data by date
    sorted_dates= sorted(dates_hourly_data.keys(), reverse=True)

    # dates_hourly_data = {key.strftime('%a, %d-%b'): value for key, value in dates_hourly_data.items()}
    dates_hourly_data = {key.strftime('%a, %d-%b'): dates_hourly_data[key] for key in sorted_dates}
    # print(dates_hourly_data.keys())
    return JsonResponse(
        {'data': dates_hourly_data}
    )

