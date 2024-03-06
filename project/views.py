from typing import Any
from django.shortcuts import render
from .models import *
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min, Count, DateTimeField, ExpressionWrapper, F 
from django.db.models.functions import TruncDate, TruncHour, Concat, TruncMinute
from django.db.models.expressions import Func, Value
from django.utils import timezone
import pytz
from django.views import View
from django.db import connection
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from django.db.utils import DatabaseError


data_table= AllSensorMeasurementsWithLocationsZephyr
# data_table= AllSensorMeasurementsWithLocationsSc
# data_table= AllPlumeMeasurements
#49, 47,29, 11
def index(request):
    sensor_ids = get_sensor_ids()
    return render(request, 'index.html',
                  context={'sensor_ids': sensor_ids})
def get_sensor_ids():
    sensor_ids = data_table.objects.values('sensor_id').distinct()
    sensor_ids = list(map(lambda x: x['sensor_id'],sensor_ids))
    return sensor_ids




'''
SensorDataView is a class-based view that handles the request for sensor data.
It is a subclass of django.views.View.


+ get()
    + request: HttpRequest
    + return: HttpResponse
    + description: 
        + The get method is called when a GET request is made to the view. It captures the parameters received in the request and calls the appropriate function to fetch the data from the database. 
'''
class SensorDataView(View):
    def get(self, request):
        requestGET = request.GET
        if requestGET:
            sensor_id1=requestGET.get('sensor_one') #sensor id
            sensor_id2=requestGET.get('sensor_two') 
            start_date=requestGET.get('start_date') #date range
            end_date=requestGET.get('end_date')
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S') #convert the date string to a datetime object
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

                #Convert the datetime objects to UTC timezone
                start_datetime = pytz.timezone('UTC').localize(start_datetime)
                end_datetime = pytz.timezone('UTC').localize(end_datetime)
            except:
                return JsonResponse(
                    {'error': 'Invalid date format'}
                )
            if sensor_id1:
                minutely_data_df = self.get_minutely_data_df(sensor_id1, start_datetime, end_datetime) #fetch minutely data
                if  type(minutely_data_df) == dict and 'error' in minutely_data_df:
                    return JsonResponse(minutely_data_df)
                minutely_data = self.convert_df_to_dict(minutely_data_df, start_datetime, end_datetime)
                print(minutely_data)
                # aqi_data = self.get_aqi_data(minutely_data_df)
                aqi_data = 'test'


                return JsonResponse(
                    {'minutely_data': minutely_data, 'aqi_data': aqi_data}
                )
            else:
                return JsonResponse(
                    {'error': 'Invalid sensor id'}
                )
        else:
            return JsonResponse(
                {'error': 'No parameters received'}
            )
        
        


    def get_minutely_data_df(self, sensor_id, start_datetime, end_datetime):
        '''
        param sensor_id: int
        param start_date: datetime
        param end_date: datetime
        return: pd.DataFrame representing the minutely data  - 5 columns: time, no2, particulatepm10, particulatepm2_5
        '''
        #This fetches the minute average data for the date range from the database and returns it as a pandas dataframe
        fields=('sensor_id', 'obs_date', 'obs_time_utc', 'no2', 'particulatepm10', 'particulatepm2_5')
        try:
            data_per_minute = (
            data_table.objects.values(*fields)
            .filter(sensor_id=sensor_id).annotate(
                datetime=ConcatDateTime(
                    F('obs_date'), Value(' '), F('obs_time_utc')
                )
            ).filter(datetime__range=[start_datetime, end_datetime])
            .annotate(minute=TruncMinute('datetime'))
            .values('minute')
            .annotate(
                no2_avg=Avg('no2'),
                # voc_avg=Avg('voc'),
                particulatepm2_5_avg=Avg('particulatepm2_5'),
                particulatepm10_avg=Avg('particulatepm10'),
                # particulatepm1_avg=Avg('particulatepm1')
            )
            .order_by('minute'))
        except DatabaseError as e:
            return {'error': 'Database error'}
        except Exception as e:
            return {'error': 'An error occurred'}

        # if not data_per_minute:
        #     return None
        if not data_per_minute:
            return None
        df=pd.DataFrame(data_per_minute)
        df.set_index('minute', inplace=True) #set the index to the minute column
        
        #sort the minutes index in ascending order and insert missing minutes with nan values
        index=pd.date_range(start=start_datetime, end=end_datetime, freq='min', tz='UTC') 
        df=df.reindex(index)
        df.index=df.index.strftime('%Y-%m-%d %H:%M:%S')

        #Replace nan values with Python None
        df=df.replace(np.nan,None)
        return df
    
    def convert_df_to_dict(self, df, start_datetime, end_datetime):
        '''
        param df: pd.DataFrame
        param start_datetime: datetime
        param end_datetime: datetime
        return: dict - a dictionary of key- value-list pairs representing the data in the dataframe
                                        5 keys: time, no2, particulatepm10, particulatepm2_5, particulatepm1
                                        and their corresponding values
        '''
        if df is not None:
            data_as_dict = {'time': df.index.tolist()}
            data_as_dict.update({
                k.replace('_avg',''): df[k].values.tolist() for k in df
            })
        else:
            data_as_dict= {'time': pd.date_range(start=start_datetime, end=end_datetime, freq='min', tz='UTC').strftime('%Y-%m-%d %H:%M:%S').tolist(),
                                        'no2':[],'particulatepm2_5':[],'particulatepm10':[]}
        return data_as_dict

    def compute_aqi(self, df):
        '''
        param df: pd.DataFrame
        return: dict - a dictionary of key- value pairs representing the AQI values for the 3 pollutants
        '''
        #This function computes the AQI values for the 5 pollutants
        #The AQI values are computed using the formulae provided by the EPA
        #The AQI values are then categorized into the appropriate AQI category
        #The AQI values and their corresponding categories are then returned as a dictionary
        aqi_data = {}
        for pollutant in ['no2', 'particulatepm10', 'particulatepm2_5']:
            aqi_data[pollutant] = self.compute_aqi_for_pollutant(df[pollutant])
        return aqi_data

class ConcatDateTime(Func):
    '''
    This class is used to concatenate the date and time fields in the database to create a temporal datetime field in the database.
    It is a subclass of django.db.models.expressions.Func'''
    function = 'TO_TIMESTAMP'
    template = "%(function)s(CONCAT(%(expressions)s), 'YYYY-MM-DD HH24:MI:SS')"
    output_field = DateTimeField()


# class AQI:
    
#     def no2_aqi(self, c):
#         if c < 0:
#             return None
#         elif c <= 53:
#             return self.compute_aqi(c, 0, 53, 0, 50)
#         elif c <= 100:
#             return self.compute_aqi(c, 54, 100, 51, 100)
#         elif c <= 360:
#             return self.compute_aqi(c, 101, 360, 101, 150)
#         elif c <= 649:
#             return self.compute_aqi(c, 361, 649, 151, 200)
#         elif c <= 1249:
#             return self.compute_aqi(c, 650, 1249, 201, 300)
#         elif c <= 2049:
#             return self.compute_aqi(c, 1250, 2049, 301, 400)
#         else:
#         return self.compute_aqi(c, 2050, 4049, 401, 500)


    # def get(self, request):
    #     requestGET = request.GET
    #     sensor_id1=requestGET.get('sensor_id1')
    #     sensor_id2=requestGET.get('sensor_id2')
    #     comparing_average_trend=requestGET.get('compare_average_trend')
    #     date=requestGET.get('date')
    #     start_date=requestGET.get('start_date')
    #     end_date=requestGET.get('end_date')
    #     chart_type=requestGET.get('chart_type')
    #     if date:    date = datetime.strptime(date, '%Y-%m-%d')
    #     date = pytz.timezone('UTC').localize(date)
    #     # print(date)
        
    #     if start_date and end_date:    start_date, end_date = datetime.strptime(start_date, '%Y-%m-%d').date(), datetime.strptime(end_date, '%Y-%m-%d').date()

    #     sensorids= [sensor_id1, sensor_id2] if sensor_id2 else [sensor_id1] 
        
    #     if date: 
            
    #         if comparing_average_trend==True:
    #             daily_average_data=get_daily_average_data(sensorids,date)
    #         else:
    #             data={}
    #             # sensorids= ['24','47']
    #             # date=pytz.timezone('UTC').localize(datetime(2024, 1, 20))
                
    #             if sensor_id1 and sensor_id2 and chart_type=='Bar':
    #                 data,correlations=get_correlation(sensorids,date)
    #                 return JsonResponse(
    #                     {'data': data, 'correlations': correlations}
    #                 )
    #             else:
    #                 data, correlations=get_24_hours_data_by_minute(sensorids,date)
    #                 # correlations=None
    #                 if correlations:
    #                     # print(data)
    #                     return JsonResponse(
    #                         {'data': data, 'correlations': correlations}
    #                     )
    #                 else:
    #                     return JsonResponse(
    #                     {'data': data}
    #                     )

    #         # data=get_24_hours_data_by_minute(sensorids,date)

# class ConcatDateTime(Func):
#     function = 'TO_TIMESTAMP'
#     template = "%(function)s(CONCAT(%(expressions)s), 'YYYY-MM-DD HH24:MI:SS')"
#     output_field = DateTimeField()

# def get_correlation(sensor_ids, date):
#     #This fetches the last 24 hours data averaged by minute
#     start_datetime=date
#     end_datetime = start_datetime + timezone.timedelta(days=1)
#     data={'no2':{},'voc':{},'particulatepm10':{},'particulatepm2_5':{},'particulatepm1':{}}
#     correlations={'no2':None,'voc':None,'particulatepm10':None,'particulatepm2_5':None,'particulatepm1':None}
#     df1= get_minute_average_data(sensor_ids[0], start_datetime, end_datetime)
#     df2= get_minute_average_data(sensor_ids[1], start_datetime, end_datetime)
#     if df1 is not None and df2 is not None:
#     #Calculate the difference
#         for column in df1.columns:
#             #rsubtract the two dataframes for each column (note: the subtraction implicitly gives NaN for missing values)
#             difference = abs(df1[column] - df2[column])
#             difference = difference.dropna().astype(int) #drop the nan values and convert to int
#             counts=difference.value_counts().to_dict()
#             data[column.replace('_avg','')]=counts
#             correlation= df1[column].corr(df2[column])
#             if not np.isnan(correlation):
#                 correlations[column.replace('_avg','')]=round(correlation, 2)

#         # Plot the histogram
#         # # plt.figure
#         # plt.hist(difference_no2, bins=20, alpha=0.5, label='Difference in NO2')
#         # plt.legend(loc='upper right')
#         # plt.xlabel('Difference in NO2')
#         # plt.ylabel('Frequency')
#         # plt.show()
#         return data, correlations
#     else:
#         return {},{}

# def get_minute_average_data(sensor_id, start_datetime, end_datetime):
#     #This fetches the minute average data for the date range from the database and returns it as a pandas dataframe
#     fields=('sensor_id', 'obs_date', 'obs_time_utc', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1')
#     data_per_minute = (
#     data_table.objects.values(*fields)
#     .filter(sensor_id=sensor_id).annotate(
#         datetime=ConcatDateTime(
#             F('obs_date'), Value(' '), F('obs_time_utc')
#         )
#     ).filter(datetime__range=[start_datetime, end_datetime])
#     .annotate(minute=TruncMinute('datetime'))
#     .values('minute')
#     .annotate(
#         no2_avg=Avg('no2'),
#         voc_avg=Avg('voc'),
#         particulatepm10_avg=Avg('particulatepm10'),
#         particulatepm2_5_avg=Avg('particulatepm2_5'),
#         particulatepm1_avg=Avg('particulatepm1')
#     )
#     .order_by('minute'))
#     if not data_per_minute:
#         return None
            
#     df=pd.DataFrame(data_per_minute)
#     df.set_index('minute', inplace=True)
#     index=pd.date_range(start=start_datetime, end=end_datetime, freq='min', tz='UTC')
#     df=df.reindex(index)
#     df.index=df.index.strftime('%Y-%m-%d %H:%M:%S')
#     #convert nan to None
#     df=df.replace(np.nan,None)
#     return df

# def get_24_hours_data_by_minute(sensor_ids,date):
#     #This fetches the last 24 hours data averaged by minute
#     start_datetime=date
#     end_datetime = start_datetime + timezone.timedelta(days=1)
    
#     data=[]
#     dfs=[]
#     for sensor_id in sensor_ids:
#         df= get_minute_average_data(sensor_id, start_datetime, end_datetime)
#         dfs.append(df)
#         if df is not None:
#             this_data = {'time': df.index.tolist()}
#             this_data.update({
#                 k.replace('_avg',''): df[k].values.tolist() for k in df
#             })
#         else:
#             this_data= {'time': pd.date_range(start=start_datetime, end=end_datetime, freq='min', tz='UTC').strftime('%Y-%m-%d %H:%M:%S').tolist(),
#                                         'no2':[],'voc':[],'particulatepm10':[],'particulatepm2_5':[],'particulatepm1':[]}
            
        
#         # print(df)
#         data.append({sensor_id:this_data})
#     if len(dfs)>1:
#         df1, df2 = dfs
#         correlations={'no2':None,'voc':None,'particulatepm10':None,'particulatepm2_5':None,'particulatepm1':None}
#         if df1 is not None and df2 is not None:
#             for column in df1.columns:
#                 correlation= df1[column].corr(df2[column])
#                 if not np.isnan(correlation):
#                     correlations[column.replace('_avg','')]=round(correlation, 2)
#             return data, correlations

#         # #Feed the data into the data template
#         # for entry in data_per_minute:
#         #     minute = entry['minute']
#         #     for sensor_type in ['no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1']:
#         #         data_template[datetime.strftime(minute, '%Y-%m-%d %H:%M:%S')][sensor_type]=entry[f"{sensor_type}_avg"]
#         # data.append({sensor_id:data_template})


#     return data, None

