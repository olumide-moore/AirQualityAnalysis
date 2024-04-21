from ..services.sensor_data_fetcher import SensorDataFetcher
from ..services.data_processor import DataProcessor
from ..services.aqi_calculator import AQICalculator
from ..services import sensors_metadata

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json

from datetime import datetime
import numpy as np

# import time

fetcher= SensorDataFetcher()

@login_required
def initialize_page(request):
    '''
    This function is used to render the home page
    On render, it fetches all the sensor types and their ids from the sensors_metadata module'''
    sensors= sensors_metadata.get_all_sensor_types()
    all_sensor_types= {
        typeid: {'name': name, 'ids': sensors_metadata.get_sensor_ids(typeid)} for typeid, name in sensors.items()
    }
    return render(request, 'home.html',
                  context={'all_sensor_types': all_sensor_types,
                            'all_sensor_types_json': json.dumps(all_sensor_types)}
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
    Fetches the raw data from the database for the given sensor_id and for the given date.
    If the data is not available in the cache, it fetches the data from the database and updates the cache.
    :param sensor_type: str - the type of the sensor
    :param sensor_id: int - the id of the sensor
    :param date: str - the date in the format 'YYYY-MM-DD'
    :return: JsonResponse - a json response containing the data for the given date - last updated date, rawdata, hourly averages, average data, aqi data
    :side effect: updates the cache with the fetched data
    """
    try:        
        date = datetime.strptime(date, '%Y-%m-%d').date() #convert the date to datetime.date object
    except:
        return JsonResponse(
            {'error': 'Invalid date format'}
        )

        #Check if sensor_type or sensor_id has changed
    if fetcher.get_sensor_type() != sensor_type or fetcher.get_sensor_id() != sensor_id:
        fetcher.set_sensor_type(sensor_type) #update the sensor type and sensor id in the fetcher
        fetcher.set_sensor_id(sensor_id)
    last_updated = fetcher.fetch_last_updated() #fetch the last updated date and time
    if date != date.today() and date in fetcher.cache_rawdata: #Check if the data for the given date is available in the cache
        rawdata = fetcher.cache_rawdata[date]
        hourly_avgs = fetcher.cache_hourlyavgs[date]
    else:
        rawdata = fetcher.fetch_raw_data([date]).get(date) #fetch the raw data for the given date
        hourly_avgs = DataProcessor.calc_hrly_avgs_all_pollutants(rawdata, date) #calculate the hourly averages
        fetcher.update_cache({date: rawdata}, {date: hourly_avgs}) #update the cache with the fetched data
    no2_hourly_avgs= DataProcessor.calc_hrly_avgs_single_pollutant(rawdata['no2'], minute_threshold= 45) #calculate the hourly averages for NO2
    no2_hourly_avg_max = no2_hourly_avgs.max() #get the maximum hourly average for NO2
    if no2_hourly_avg_max in [np.nan, None]:   no2_hourly_avg_max = None  #if the maximum hourly average is np.nan, set it to None

    pm2_5_24houravg = DataProcessor.calc_24hr_avg_single_pollutant(rawdata['pm2_5'],minute_threshold= 1080) #calculate the 24 hour average for PM2.5
    pm10_24houravg = DataProcessor.calc_24hr_avg_single_pollutant(rawdata['pm10'],minute_threshold= 1080) #calculate the 24 hour average for PM10

        #calculate the AQI for NO2, PM2.5 and PM10
    aqi_data = {'no2': AQICalculator.get_no2_index(no2_hourly_avg_max), 'pm2_5': AQICalculator.get_pm2_5_index(pm2_5_24houravg), 'pm10': AQICalculator.get_pm10_index(pm10_24houravg)}

        #round off the average values to 2 decimal places
    no2_hourly_avg_max = round(no2_hourly_avg_max, 2) if no2_hourly_avg_max else None
    pm2_5_24houravg = round(pm2_5_24houravg, 2) if pm2_5_24houravg else None
    pm10_24houravg = round(pm10_24houravg, 2) if pm10_24houravg else None
    avg_data = {'no2': no2_hourly_avg_max, 'pm2_5': pm2_5_24houravg, 'pm10': pm10_24houravg}

    rawdata_dict = DataProcessor.convert_df_to_dict(rawdata)
    return JsonResponse(
        {'last_updated': last_updated, 
        'rawdata': rawdata_dict,
        'hourly_avgs':hourly_avgs, 
        'avg_data': avg_data,
        'aqi_data': aqi_data
        }
    )

@login_required
def get_hourlyavgs_across_dates(request, sensor_type, sensor_id, dates):
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
        dates = dates.split(',') #split the dates string by comma
        dates = [datetime.strptime(date, '%Y-%m-%d').date() for date in dates] #convert the dates to datetime.date objects
    except:
        return JsonResponse(
            {'error': 'Invalid date format'}
        )
        #Check if sensor_type or sensor_id has changed
    if fetcher.get_sensor_type() != sensor_type or fetcher.get_sensor_id() != sensor_id:
        fetcher.set_sensor_type(sensor_type) #update the sensor type and sensor id in the fetcher
        fetcher.set_sensor_id(sensor_id)
    dates_hourly_data={} #data stored in format {'Mon, 01-Jan': { 'no2': {0: 10, 1: 20, ...}, 'pm2_5': {0: 10, 1: 20, ...}, 'pm10': {0: 10, 1: 20, ...}}, ...}
    #Check if the data for the given dates is available in the cache
    for date in list(fetcher.cache_hourlyavgs.keys()):
        if date != date.today() and date in dates:
            dates_hourly_data[date]= fetcher.cache_hourlyavgs[date]
            dates.remove(date) #remove the date from the list of dates as it is already available in the cache
    if dates: #If the data for some dates is not available in the cache, fetch the data from the database
        dates_raw_data = fetcher.fetch_raw_data(dates)
        for date, data in dates_raw_data.items():
            dates_hourly_data[date]= DataProcessor.calc_hrly_avgs_all_pollutants(data, date)
        #update the cache
        fetcher.update_cache(dates_raw_data, dates_hourly_data)
    #sort the data by date
    sorted_dates= sorted(dates_hourly_data.keys(), reverse=True)

    #convert the dates_hourly_data dictionary to a dictionary with dates in the format 'Mon, 01-Jan'
    dates_hourly_data = {key.strftime('%a, %d-%b'): dates_hourly_data[key] for key in sorted_dates}
    return JsonResponse(
        {'data': dates_hourly_data}
    )

