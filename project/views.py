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

# data_table= AllSensorMeasurementsWithLocationsZephyr
# data_table= AllSensorMeasurementsWithLocationsSc
data_table= AllPlumeMeasurements
#49, 47,29, 11
def home(request):
    sensor_types= get_sensor_types()
    return render(request, 'home.html',
                  context={'sensor_types': sensor_types})

def compare(request):
    sensor_ids = get_sensor_ids()
    return render(request, 'compare.html',
                  context={'sensor_ids': sensor_ids})
def get_sensor_types():
    sensor_types  = Sensortypes.objects.values('id','name').distinct()
    sensor_types = dict(map(lambda x: (x['id'], x['name']),sensor_types))
    return sensor_types
    

def get_sensor_ids(request, type_id):
    sensors = Sensors.objects.values('id', 'lookup_id', 'active', 'time_created', 'stationary_box', 'user_id').filter(type_id=type_id)
    return JsonResponse(
        {'sensors': list(sensors)}
    )



'''
SensorDataView is a class-based view that handles the request for sensor data.
It is a subclass of django.views.View.


+ get()
    + request: HttpRequest
    + return: HttpResponse
    + description: 
        + The get method is called when a GET request is made to the view. It captures the parameters received in the request and calls the appropriate function to fetch the data from the database. 
'''

def get_sensor_data(request, sensor_type, sensor_id, start, end):
    try:
        #Test data
        # start='2024-01-22 00:00:00'
        # end='2024-01-22 23:59:59'
        sensor_type='Zephyr'
        sensor_id = 60
        #End test data


        start_datetime = datetime.strptime(start, '%Y-%m-%d %H:%M:%S') #convert the date string to a datetime object
        end_datetime = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')

        #Convert the datetime objects to UTC timezone
        start_datetime = pytz.timezone('UTC').localize(start_datetime)
        end_datetime = pytz.timezone('UTC').localize(end_datetime)

        # sensorid= '47'
        # start_datetime=pytz.timezone('UTC').localize(datetime(2024, 1, 20, 0, 0, 0))
        # end_datetime=pytz.timezone('UTC').localize(datetime(2024, 1, 20, 23, 59, 59))
    except:
        return JsonResponse(
            {'error': 'Invalid date format'}
        )
    if sensor_id:
        setTable(sensor_type)
        sensor = Sensor(sensor_id, ['no2', 'particulatepm10', 'particulatepm2_5'])
        # minutely_data_df = self.get_minutely_data_df(sensorid, start_datetime, end_datetime) #fetch minutely data
        # if  type(minutely_data_df) == dict and 'error' in minutely_data_df:
        #     return JsonResponse(minutely_data_df)
        # # print(minutely_data)
        # aqi_data = aqi_obj.compute_aqi()
        # # aqi_data = 'test'
        #update start time to the last 7 days
        rawdata_7lastdays = sensor.getRawData_Last7Days(end_datetime)
        hourly_avgs_7lastdays = {key: sensor.getHourlyAverages(value, datetime.combine(key, datetime.min.time()), datetime.combine(key, datetime.max.time())) for key, value in rawdata_7lastdays.items()}
        hourly_avgs_7lastdays_dict = {key.strftime("%a, %d-%b"): convert_df_to_dict(value) for key, value in hourly_avgs_7lastdays.items()}

        rawdata_samedaylast7weeks = sensor.getRawData_SameDayLast7Weeks(end_datetime)
        hourly_avgs_samedaylast7weeks = {key: sensor.getHourlyAverages(value, datetime.combine(key, datetime.min.time()), datetime.combine(key, datetime.max.time())) for key, value in rawdata_samedaylast7weeks.items()}
        hourly_avgs_samedaylast7weeks_dict = {key.strftime("%a, %d-%b"): convert_df_to_dict(value) for key, value in hourly_avgs_samedaylast7weeks.items()}
    

        rawdata_requested_date = rawdata_7lastdays[end_datetime.date()]
        minutely_avgs_requested_date = sensor.getMinutelyAverages(rawdata_requested_date,start_datetime, end_datetime)
        hourly_avgs_requested_date = sensor.getHourlyAverages(rawdata_requested_date, start_datetime, end_datetime)
        minutely_avgs_dict = convert_df_to_dict(minutely_avgs_requested_date)
        hourly_avgs_dict = convert_df_to_dict(hourly_avgs_requested_date)
        hourly_aqis = aqi_obj.compute_hourly_aqis(hourly_avgs_dict)
        last_updated = sensor.getLastUpdatedTime()
        # print(last_updated)

        no2_hourly_avgs= sensor.getNO2_HourlyAvgs(rawdata_requested_date['no2'], minute_threshold= 45)
        no2_hourly_avg_max = no2_hourly_avgs.max()
        if no2_hourly_avg_max in [np.nan, None]:
            no2_hourly_avg_max = None
        pm2_5_24houravg = sensor.getPM2_5_24HourAvg(rawdata_requested_date['pm2_5'],minute_threshold= 1080)
        pm10_24houravg = sensor.getPM10_24HourAvg(rawdata_requested_date['pm10'],minute_threshold= 1080)

        aqi_data = {'no2': aqi_obj.getNO2Index(no2_hourly_avg_max),
                    'pm2_5': aqi_obj.getPM2_5Index(pm2_5_24houravg),
                    'pm10': aqi_obj.getPM10Index(pm10_24houravg)
                    }
        no2_hourly_avg_max = round(no2_hourly_avg_max, 2) if no2_hourly_avg_max else None
        pm2_5_24houravg = round(pm2_5_24houravg, 2) if pm2_5_24houravg else None
        pm10_24houravg = round(pm10_24houravg, 2) if pm10_24houravg else None
        # print(minutely_avgs_dict, hourly_avgs_dict, hourly_aqis, aqi_data)
        return JsonResponse(
            {'minutely_avgs': minutely_avgs_dict, 'hourly_avgs':hourly_avgs_dict, 'last_updated': last_updated,
             'hourly_aqis':hourly_aqis,
             'avg_data': {'no2': no2_hourly_avg_max, 'pm2_5': pm2_5_24houravg, 'pm10': pm10_24houravg},
              'aqi_data': aqi_data, 'hourly_avgs_7lastdays': hourly_avgs_7lastdays_dict, 
              'hourly_avgs_samedaylast7weeks': hourly_avgs_samedaylast7weeks_dict
              }
        )
    else:
        return JsonResponse(
            {'error': 'Invalid sensor id'}
        )
    
def convert_df_to_dict(df):
    '''
    param df: pd.DataFrame
    return: dict - a dictionary of key- value-list pairs representing the data in the dataframe
                                    5 keys: time, no2, pm10, pm2_5, pm1
                                    and their corresponding values
    '''
    data_as_dict = df.to_dict(orient='list')
    data_as_dict['time'] = df.index.strftime('%Y-%m-%d %H:%M:%S').tolist() #convert the index to a list of strings
    return data_as_dict

aqi_obj = AQI()