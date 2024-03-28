from .models import *

from django.db.models import Avg, DateTimeField, F 
from django.db.models.functions import TruncMinute
from django.db.models.expressions import Func, Value

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


TABLE= None

def setTable(sensor_type):
    global TABLE
    if sensor_type == 'Zephyr':
        TABLE= AllSensorMeasurementsWithLocationsZephyr
    elif sensor_type == 'SensorCommunity':
        TABLE= AllSensorMeasurementsWithLocationsSc
    elif sensor_type == 'Plume':
        TABLE= AllPlumeMeasurements
    else:
        TABLE= None
    return TABLE
class Sensor():
    def __init__(self, sensor_id, requiredConcentrations):
        self.SENSOR_ID = sensor_id
        self.requiredConcentrations = requiredConcentrations
        self.cachedRawData = {}
    
    def getLastUpdatedTime(self):
        if TABLE is None: return None
        try:
            last_updated = TABLE.objects.values('obs_date','obs_time_utc').filter(sensor_id=self.SENSOR_ID).latest('obs_date', 'obs_time_utc')
        except TABLE.DoesNotExist:
            last_updated = None

        return last_updated

    # def getRawData(self, start, end):
    #     ''' param start: datetime
    #         param end: datetime
    #         return: pd.DataFrame
    #         This function fetches the raw data from the database for the given sensor_id and the required concentrations between the start and end datetime
    #         '''
    #     if TABLE:
    #         rawdata = (
    #         TABLE.objects.values('obs_date', 'obs_time_utc', *self.requiredConcentrations)
    #         .filter(sensor_id=self.SENSOR_ID)
    #         .annotate( 
    #             datetime = ConcatDateTime(
    #             F('obs_date'), 
    #             Value(' '), 
    #             F('obs_time_utc')
    #             )
    #         ).filter(datetime__range=(start, end)).order_by('datetime')
    #         )
    #     else:
    #         rawdata = {'datetime': []}
    #         rawdata.update({c: [] for c in self.requiredConcentrations})
    #     rawdata = pd.DataFrame(rawdata, columns=['datetime', *self.requiredConcentrations]) #convert the queryset to a pandas dataframe
    #     rawdata.rename(columns={'particulatepm2_5':'pm2_5', 'particulatepm10':'pm10', 'particulatepm1':'pm1'}, inplace=True)
    #     rawdata['datetime'] = pd.to_datetime(rawdata['datetime']) #convert the datetime column to a pandas datetime object
    #     rawdata.set_index('datetime', inplace=True)
    #     self.cachedRawData = rawdata
    #     # print(rawdata)
    #     return rawdata
    def getRawData_forSetDates(self, dates):
        ''' param dates: list of datetime
            return: pd.DataFrame
            This function fetches the raw data from the database for the given sensor_id and the required concentrations for the given dates
            '''
        for date in list(self.cachedRawData.keys()): 
            if date not in dates: 
                del self.cachedRawData[date] #delete the cached data that is not in the last 7 days
            else:
                dates.remove(date)  #remove the dates that are already cached
        if TABLE:
            rawdata = (
            TABLE.objects.values('obs_date', 'obs_time_utc', *self.requiredConcentrations)
            .filter(sensor_id=self.SENSOR_ID)
            .annotate( 
                datetime = ConcatDateTime(
                F('obs_date'), 
                Value(' '), 
                F('obs_time_utc')
                )
            ).filter(obs_date__in=dates).order_by('datetime')
            )
        else:
            rawdata = {'datetime': []}
            rawdata.update({c: [] for c in self.requiredConcentrations})
        rawdata = pd.DataFrame(rawdata, columns=['datetime', *self.requiredConcentrations]) #convert the queryset to a pandas dataframe
        rawdata.rename(columns={'particulatepm2_5':'pm2_5', 'particulatepm10':'pm10', 'particulatepm1':'pm1'}, inplace=True)
        rawdata['datetime'] = pd.to_datetime(rawdata['datetime']) #convert the datetime column to a pandas datetime object
        rawdata.set_index('datetime', inplace=True)
        data_by_day = {}
        for date in dates:
            data_by_day[date] = rawdata[rawdata.index.date == date]
        self.cachedRawData = data_by_day
        return data_by_day
    
    def getRawData_Last7Days(self, end):
        ''' param end: datetime
            return: pd.DataFrame
            This function fetches the raw data from the database for the given sensor_id and the required concentrations for last 7 days till the end datetime and the end datetime
            '''
        dates= [end.date() - timedelta(days=i) for i in range(7)]
        return self.getRawData_forSetDates(dates)

        
    def getRawData_SameDayLast7Weeks(self, end):
        ''' param end: datetime
            return: pd.DataFrame
            This function fetches the raw data from the database for the given sensor_id and the required concentrations for the same day of the week for the last 7 weeks till the end datetime and the end datetime
            '''
        dates= [end.date() - timedelta(weeks=i) for i in range(7)] #This gets the dates for the same day of the week for the last 7 weeks
        return self.getRawData_forSetDates(dates)


    def getMinutelyAverages(self, rawdata, start, end):
        '''
        param rawdata: pd.DataFrame
        param start: datetime
        param end: datetime
        param returnType: str
        return: pd.DataFrame
        This function calculates the average concentration of the pollutants for each minute between the start and end datetime
        '''
        index=pd.date_range(start=start, end=end, freq='min', tz='UTC')
        #group the data by minute and calculate the average concentration for each minute
        data_per_minute = rawdata.resample('min').mean()
        #insert missing minutes with None values
        data_per_minute = data_per_minute.reindex(index)
        data_per_minute.replace(np.nan, None, inplace=True) #replace nan values with None
        return data_per_minute
    
    def getHourlyAverages(self, rawdata, start, end, minute_threshold=45):
        '''
        param rawdata: pd.DataFrame
        param start: datetime
        param end: datetime
        param returnType: str
        return: pd.DataFrame
        This function calculates the average concentration of the pollutants for each hour between the start and end datetime
        '''
        index=pd.date_range(start=start, end=end, freq='h', tz='UTC')
        #group the data by hour and calculate the average concentration for each hour
        data_grouped_by_hour = rawdata.resample('h')
        data_per_hour = data_grouped_by_hour.apply(lambda x: x.mean() if x.count() >= minute_threshold else None)
        #insert missing hours with None values
        data_per_hour = data_per_hour.reindex(index)
        data_per_hour.replace(np.nan, None, inplace=True)
        return data_per_hour        
    
    def getNO2_HourlyAvgs(self, no2_rawdata, minute_threshold=45):
        '''
        param no2_rawdata: pd.Series
        param minute_threshold: int
        return: float - the average NO2 concentration
        This function checks if there is atleast 75% (45minutes) of no2 data of the hourly data required, then calculates the average hourly no2 concentration and returns the maximum value
        '''
        no2_grouped_by_hour = no2_rawdata.resample('h')
        #get the hourly mean of the hours >= 45 minutes
        no2_hourlyavgs = no2_grouped_by_hour.apply(lambda x: x.mean() if x.count() >= minute_threshold else None)
        return no2_hourlyavgs
    
    def getPM2_5_24HourAvg(self, pm2_5_rawdata, minute_threshold=1080):
        '''
        param pm2_5_rawdata: pd.Series
        param minute_threshold: int
        return: float - the average PM2.5 concentration
        This function checks if there is atleast 75% (1080mins or 18hours ) of pm2.5 data of the 24hour data required, then calculates the average pm2.5 concentration
        '''
        if pm2_5_rawdata.count() >= minute_threshold:
            return pm2_5_rawdata.mean()
        
    def getPM10_24HourAvg(self, pm10_rawdata, minute_threshold=1080):
        '''
        param pm10_rawdata: pd.Series
        param minute_threshold: int
        return: float - the average PM10 concentration
        This function checks if there is atleast 75% (1080mins or 18hours ) of pm10 data of the 24hour data required, then calculates the average pm10 concentration
        '''
        if pm10_rawdata.count() >= minute_threshold:
            return pm10_rawdata.mean()
   

class ConcatDateTime(Func):
    '''
    This class is used to concatenate the date and time fields in the database to create a temporal datetime field in the database.
    It is a subclass of django.db.models.expressions.Func'''
    function = 'TO_TIMESTAMP'
    template = "%(function)s(CONCAT(%(expressions)s), 'YYYY-MM-DD HH24:MI:SS')"
    output_field = DateTimeField()


class AQI:
    def __init__(self):
        self.NO2_BREAKPOINTS = [67, 134, 200, 267, 334, 400, 467, 534, 600]
        self.PM2_5_BREAKPOINTS = [11, 23, 35, 41, 47, 53, 58, 64, 70]
        self.PM10_BREAKPOINTS = [16, 33, 50, 58, 66, 75, 83, 91, 100]
    
    def getNO2Index(self, no2_avg):
        '''
        param no2_avg: float
        return: int - the AQI value
        '''
        if no2_avg == None or no2_avg < 0: return None
        for index, breakpoint in enumerate(self.NO2_BREAKPOINTS):
            if no2_avg <= breakpoint:
                return index+1
        return 10
    
    def getPM2_5Index(self, pm2_5_avg):
        '''
        param pm2_5_avg: float
        return: int - the AQI value
        '''
        if pm2_5_avg == None or pm2_5_avg < 0: return None
        for index, breakpoint in enumerate(self.PM2_5_BREAKPOINTS):
            if pm2_5_avg <= breakpoint:
                return index+1
        return 10
    
    def getPM10Index(self, pm10_avg):
        '''
        param pm10_avg: float
        return: int - the AQI value
        '''
        if pm10_avg == None or pm10_avg < 0: return None
        for index, breakpoint in enumerate(self.PM10_BREAKPOINTS):
            if pm10_avg <= breakpoint:
                return index+1
        return 10
         
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
                        hourly_aqis[pollutant] = list(map(self.getNO2Index, hourly_avgs[pollutant]))
                    elif pollutant == 'pm2_5':
                        hourly_aqis[pollutant] = list(map(self.getPM2_5Index, hourly_avgs[pollutant]))
                    elif pollutant == 'pm10':
                        hourly_aqis[pollutant] = list(map(self.getPM10Index, hourly_avgs[pollutant]))
            return hourly_aqis  
        


