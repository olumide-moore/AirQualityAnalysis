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

# data_table= AllSensorMeasurementsWithLocationsZephyr
# data_table= AllSensorMeasurementsWithLocationsSc
data_table= AllPlumeMeasurements
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

                # sensor_id1= '47'
                # start_datetime=pytz.timezone('UTC').localize(datetime(2024, 1, 20, 0, 0, 0))
                # end_datetime=pytz.timezone('UTC').localize(datetime(2024, 1, 20, 23, 59, 59))
                
            except:
                return JsonResponse(
                    {'error': 'Invalid date format'}
                )
            if sensor_id1:
                minutely_data_df = self.get_minutely_data_df(sensor_id1, start_datetime, end_datetime) #fetch minutely data
                if  type(minutely_data_df) == dict and 'error' in minutely_data_df:
                    return JsonResponse(minutely_data_df)
                # print(minutely_data)
                aqi_obj.set_dataframe(minutely_data_df)
                aqi_data = aqi_obj.compute_aqi()
                # aqi_data = 'test'
                hourly_avgs=compute_hourly_avgs(minutely_data_df)
                hourly_aqis = aqi_obj.compute_hourly_aqis(hourly_avgs)

                linechart_minutely_data = self.convert_df_to_dict(minutely_data_df, start_datetime, end_datetime)
                return JsonResponse(
                    {'minutely_data': linechart_minutely_data, 'hourly_avgs':hourly_avgs, 'hourly_aqis':hourly_aqis, 'aqi_data': aqi_data}
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
        return: pd.DataFrame representing the minutely data  - 5 columns: time, no2, pm10, pm2_5
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
                no2=Avg('no2'),
                # voc=Avg('voc'),
                pm2_5=Avg('particulatepm2_5'),
                pm10=Avg('particulatepm10'),
                # pm1=Avg('particulatepm1')
            )
            .order_by('minute'))
        except DatabaseError as e:
            return {'error': 'Database error'}
        except Exception as e:
            return {'error': 'An error occurred'}

        # if not data_per_minute:
        #     return None
        index=pd.date_range(start=start_datetime, end=end_datetime, freq='min', tz='UTC') 
        if not data_per_minute:
            df= pd.DataFrame(index=index, columns=['no2', 'pm10', 'pm2_5'])
        else:
            df=pd.DataFrame(data_per_minute)
            df.set_index('minute', inplace=True) #set the index to the minute column
            
            #sort the minutes index in ascending order and insert missing minutes with nan values
            df=df.reindex(index)
            # df.index=df.index.strftime('%Y-%m-%d %H:%M:%S')

        #Replace nan values with Python None
        df=df.replace(np.nan,None)
        return df
    
    def convert_df_to_dict(self, df, start_datetime, end_datetime):
        '''
        param df: pd.DataFrame
        param start_datetime: datetime
        param end_datetime: datetime
        return: dict - a dictionary of key- value-list pairs representing the data in the dataframe
                                        5 keys: time, no2, pm10, pm2_5, pm1
                                        and their corresponding values
        '''
        if df is not None:
            data_as_dict = {'time': df.index.strftime('%Y-%m-%d %H:%M:%S').tolist()}
            data_as_dict.update({
                k: df[k].values.tolist() for k in df
            })
        return data_as_dict

class ConcatDateTime(Func):
    '''
    This class is used to concatenate the date and time fields in the database to create a temporal datetime field in the database.
    It is a subclass of django.db.models.expressions.Func'''
    function = 'TO_TIMESTAMP'
    template = "%(function)s(CONCAT(%(expressions)s), 'YYYY-MM-DD HH24:MI:SS')"
    output_field = DateTimeField()

def compute_hourly_avgs(df):
    '''
    param df: pd.DataFrame
    return: dict - with values as lists of hours, corresponding averages of NO2, PM2.5 and PM10 concentration
    This function gives the average hourly concentration of the 3 pollutants
    '''
    hourly_avg = df.resample('h').mean()
    hourly_avg=hourly_avg.replace(np.nan, None)
    time=hourly_avg.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
    no2_hourly_avg = hourly_avg['no2'].to_list()
    pm2_5_hourly_avg = hourly_avg['pm2_5'].to_list()
    pm10_hourly_avg = hourly_avg['pm10'].to_list()
    return {
        'time': time,
        'no2': no2_hourly_avg,
        'pm2_5': pm2_5_hourly_avg,
        'pm10': pm10_hourly_avg
    }
    
    # #convert the no2 average to python dict
    # avg_data['no2'].index = avg_data['no2'].index.strftime('%Y-%m-%d %H:%M:%S')
    # avg_data['no2'] = avg_data['no2'].to_dict()
    # #convert
    # avg_data['no2'].index = avg_data['no2'].index.strftime('%Y-%m-%d %H:%M:%S')
    # avg_data['no2'] = avg_data['no2'].to_dict()
    # #convert
def getLastRecorded(sensor_id):
    try:
        last_recorded = data_table.objects.filter(sensor_id=sensor_id).latest('obs_date', 'obs_time_utc')
    except data_table.DoesNotExist:
        last_recorded = None
    return last_recorded

class AQI:
    def __init__(self):
        self.no2_breakpoints = [67, 134, 200, 267, 334, 400, 467, 534, 600]
        self.pm2_5_breakpoints = [11, 23, 35, 41, 47, 53, 58, 64, 70]
        self.pm10_breakpoints = [16, 33, 50, 58, 66, 75, 83, 91, 100]

        self.dataframe = None
    
    # def get_no2_average(self, df):
    #     '''
    #     param df: pd.DataFrame
    #     return: float - the average NO2 concentration
    #     This function checks if there is atleast 75% (45minutes) of no2 data of the hourly data required, then calculates the average no2 concentration
    #     '''
        #remove the nan values and count the number of non-nan values for the given hour
    #     if df['no2'].count() >= 45:
    #         return df['no2'].mean()
    #     else:
    #         return None
        
    def set_dataframe(self, df):
        self.dataframe = df

    def get_dataframe(self):
        return self.dataframe
    
    def compute_averages(self):
        '''
        return: dict - a dictionary of key- value pairs representing the average concentrations of the 3 pollutants
        This function computes the average concentrations of the 3 pollutants
        '''
        # #This function computes the average concentrations of the 3 pollutants
        # #The average concentrations are then returned as a dictionary
        # return {
        #     'no2': df['no2'].mean(),
        #     'pm2_5': df['pm2_5'].mean(),
        #     'pm10': df['pm10'].mean()
        # }
        return {
            'no2': self.compute_no2_hourly_avg(),
            'pm2_5': self.compute_pm2_5_24_hour_avg(),
            'pm10': self.compute_pm10_24_hour_avg()
        }

    def compute_aqi(self):
        '''
        return: dict - a dictionary of key- value pairs representing the AQI values for the 3 pollutants
        '''
        # #This function computes the AQI values for the 3 pollutants
        # #The AQI values are computed using the formulae provided by the EPA
        # #The AQI values are then categorized into the appropriate AQI category
        # #The AQI values and their corresponding categories are then returned as a dictionary
        # for pollutant in ['no2', 'pm2_5', 'pm10']:
        #     aqi_data[pollutant] = self.compute_aqi_for_pollutant(df[pollutant])
        # return aqi_data
        aqi_data = {}
        no2_hourly_avg = self.compute_no2_hourly_avg()
        pm2_5_24_hour_avg = self.compute_pm2_5_24_hour_avg()
        pm10_24_hour_avg = self.compute_pm10_24_hour_avg()
        # print/("\n")
        if no2_hourly_avg.empty:
            aqi_data['no2'] = None
        else:
            no2_aqis = no2_hourly_avg.apply(self.no2_aqi)
            aqi_data['no2'] = no2_aqis.max()
            print(f"no2 avg: {no2_hourly_avg.max()} time: {no2_hourly_avg.idxmax().hour}")
        if pm2_5_24_hour_avg is None:
            aqi_data['pm2_5'] = None
        else:
            print(f"pm2.5 avg: {pm2_5_24_hour_avg}")
            aqi_data['pm2_5'] = self.pm2_5_aqi(pm2_5_24_hour_avg)
        if pm10_24_hour_avg is None:
            aqi_data['pm10'] = None
        else:
            print(f"pm10 avg: {pm10_24_hour_avg}")
            aqi_data['pm10'] = self.pm10_aqi(pm10_24_hour_avg)
        print(aqi_data)
        print("\n")

        for k, v in aqi_data.items(): #convert the aqi values to python int as numpy int is not serializable
            if v is not None:
                aqi_data[k] = int(v)
        # aqi_data= {'no2': 7, 'pm2_5': 8, 'pm10': 9}
        return aqi_data
    
    def compute_hourly_aqis(self, hourly_avgs):
        '''
        param hourly_avgs: dict
        return: dict - a dictionary of key- value pairs representing the hourly AQI values for the 3 pollutants
        This function computes the hourly AQI values for the 3 pollutants
        The AQI values and their corresponding categories are then returned as a dictionary
        '''
        if 'time' in hourly_avgs:
            hourly_aqis = {'no2':[], 'pm2_5':[], 'pm10':[]}
            for pollutant in ['no2', 'pm2_5', 'pm10']:
                if not hourly_avgs[pollutant]:
                    hourly_aqis[pollutant] = None * len(hourly_avgs['time'])
                else: 
                    if pollutant == 'no2':
                        hourly_aqis[pollutant] = list(map(self.no2_aqi, hourly_avgs[pollutant]))
                    elif pollutant == 'pm2_5':
                        hourly_aqis[pollutant] = list(map(self.pm2_5_aqi, hourly_avgs[pollutant]))
                    elif pollutant == 'pm10':
                        hourly_aqis[pollutant] = list(map(self.pm10_aqi, hourly_avgs[pollutant]))
            return hourly_aqis  
    def compute_no2_hourly_avg(self):
        '''
        return: float - the average NO2 concentration
        This function checks if there is atleast 75% (45minutes) of no2 data of the hourly data required, then calculates the average no2 concentration
        '''
        no2_grouped_by_hour = self.dataframe['no2'].resample('h')
        #get the hourly mean of the hours >= 45 minutes
        no2_hourly_avg = no2_grouped_by_hour.apply(lambda x: x.mean() if x.count() >= 45 else None)
        return no2_hourly_avg.dropna()

         
        
    def compute_pm2_5_24_hour_avg(self):
        '''
        param df: pd.DataFrame
        return: float - the average PM2.5 concentration
        This function checks if there is atleast 75% (1080mins or 18hours ) of pm2.5 data of the 24hour data required, then calculates the average pm2.5 concentration
        '''
        if self.dataframe['pm2_5'].count() >= 1080:
            return self.dataframe['pm2_5'].mean() #get the mean of non-nan values
        
    def compute_pm10_24_hour_avg(self):
        '''
        param df: pd.DataFrame
        return: float - the average PM10 concentration
        This function checks if there is atleast 75% (1080mins or 18hours ) of pm10 data of the 24hour data required, then calculates the average pm10 concentration
        '''
        if self.dataframe['pm10'].count() >= 1080:
            return self.dataframe['pm10'].mean() #get the mean of non-nan values
    # def compute_no2_hourly_avg(self):
    #     '''
    #     param df: pd.DataFrame
    #     return: float - the average NO2 concentration
    #     This function checks if there is atleast 75% (45minutes) of no2 data of the hourly data required, then calculates the average no2 concentration
    #     '''
    #     no2_grouped_by_hour = self.dataframe['no2'].resample('h')
    #     #get the hourly mean of the hours >= 45 minutes
    #     no2_hourly_avg = no2_grouped_by_hour.apply(lambda x: x.mean() if x.count() >= 45 else None)
    #     return no2_hourly_avg

    def no2_aqi(self, no2):
        '''
        param no2: float
        return: int - the AQI value
        '''
        if no2 == None or no2 < 0: return None
        for index, breakpoint in enumerate(self.no2_breakpoints):
            if no2 <= breakpoint:
                return index+1
        return 10
    
    def pm2_5_aqi(self, pm2_5):
        '''
        param pm2_5: float
        return: int - the AQI value
        '''
        if pm2_5 == None or pm2_5 < 0: return None
        for index, breakpoint in enumerate(self.pm2_5_breakpoints):
            if pm2_5 <= breakpoint:
                return index+1
        return 10
    
    def pm10_aqi(self, pm10):
        '''
        param pm10: float
        return: int - the AQI value
        '''
        if pm10 == None or pm10 < 0: return None
        for index, breakpoint in enumerate(self.pm10_breakpoints):
            if pm10 <= breakpoint:
                return index+1
        return 10
    

aqi_obj = AQI()
print('AQI object created') 


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
#     data={'no2':{},'voc':{},'pm10':{},'pm2_5':{},'pm1':{}}
#     correlations={'no2':None,'voc':None,'pm10':None,'pm2_5':None,'pm1':None}
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
#         pm10_avg=Avg('particulatepm10'),
#         pm2_5_avg=Avg('particulatepm2_5'),
#         pm1_avg=Avg('particulatepm1')
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
#                                         'no2':[],'voc':[],'pm10':[],'pm2_5':[],'pm1':[]}
            
        
#         # print(df)
#         data.append({sensor_id:this_data})
#     if len(dfs)>1:
#         df1, df2 = dfs
#         correlations={'no2':None,'voc':None,'pm10':None,'pm2_5':None,'pm1':None}
#         if df1 is not None and df2 is not None:
#             for column in df1.columns:
#                 correlation= df1[column].corr(df2[column])
#                 if not np.isnan(correlation):
#                     correlations[column.replace('_avg','')]=round(correlation, 2)
#             return data, correlations

#         # #Feed the data into the data template
#         # for entry in data_per_minute:
#         #     minute = entry['minute']
#         #     for sensor_type in ['no2', 'voc', 'pm10', 'pm2_5', 'pm1']:
#         #         data_template[datetime.strftime(minute, '%Y-%m-%d %H:%M:%S')][sensor_type]=entry[f"{sensor_type}_avg"]
#         # data.append({sensor_id:data_template})


#     return data, None

