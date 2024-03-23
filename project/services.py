from .models import *

from django.db.models import Avg, DateTimeField, F 
from django.db.models.functions import TruncMinute
from django.db.models.expressions import Func, Value

import pandas as pd
import numpy as np


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
        self.cachedRawData = None
        self.cacheStartTime = None
        self.cacheEndTime = None
    
    def getLastUpdatedTime(self):
        if TABLE is None: return None
        try:
            last_updated = TABLE.objects.values('obs_date','obs_time_utc').filter(sensor_id=self.SENSOR_ID).latest('obs_date', 'obs_time_utc')
        except TABLE.DoesNotExist:
            last_updated = None

        return last_updated

    def getRawData(self, start, end):
        if TABLE is None: return None
        if start == self.cacheStartTime and end == self.cacheEndTime and self.cachedRawData is not None:
            return self.cachedRawData
        if TABLE:
            raw_data = (
            TABLE.objects.values('obs_date', 'obs_time_utc', *self.requiredConcentrations)
            .filter(sensor_id=self.SENSOR_ID)
            .annotate( 
                datetime = ConcatDateTime(
                F('obs_date'), 
                Value(' '), 
                F('obs_time_utc')
                )
            ).filter(datetime__range=(start, end)).order_by('datetime')
            )
        else:
            raw_data = {'datetime': []}
            raw_data.update({c: [] for c in self.requiredConcentrations})
        raw_data = pd.DataFrame(raw_data, columns=['datetime', *self.requiredConcentrations]) #convert the queryset to a pandas dataframe
        raw_data.rename(columns={'particulatepm2_5':'pm2_5', 'particulatepm10':'pm10', 'particulatepm1':'pm1'}, inplace=True)
        raw_data['datetime'] = pd.to_datetime(raw_data['datetime']) #convert the datetime column to a pandas datetime object
        raw_data.set_index('datetime', inplace=True)
        # print(raw_data)
        self.cacheStartTime = start
        self.cacheEndTime = end
        self.cachedRawData = raw_data
        return raw_data
    
    def getMinutelyAverages(self, start, end):
        '''
        param start: datetime
        param end: datetime
        param returnType: str
        return: pd.DataFrame
        This function calculates the average concentration of the pollutants for each minute between the start and end datetime
        '''
        raw_data = self.getRawData(start, end)
        index=pd.date_range(start=start, end=end, freq='min', tz='UTC')
        #group the data by minute and calculate the average concentration for each minute
        data_per_minute = raw_data.resample('min').mean()
        #insert missing minutes with None values
        data_per_minute = data_per_minute.reindex(index)
        data_per_minute.replace(np.nan, None, inplace=True) #replace nan values with None
        return data_per_minute
    
    def getHourlyAverages(self, start, end, minute_threshold=45):
        '''
        param start: datetime
        param end: datetime
        param returnType: str
        return: pd.DataFrame
        This function calculates the average concentration of the pollutants for each hour between the start and end datetime
        '''
        raw_data = self.getRawData(start, end)
        index=pd.date_range(start=start, end=end, freq='h', tz='UTC')
        #group the data by hour and calculate the average concentration for each hour
        data_grouped_by_hour = raw_data.resample('h')
        data_per_hour = data_grouped_by_hour.apply(lambda x: x.mean() if x.count() >= minute_threshold else None)
        #insert missing hours with None values
        data_per_hour = data_per_hour.reindex(index)
        data_per_hour.replace(np.nan, None, inplace=True)
        return data_per_hour        
    
    def getNO2_HourlyAvgs(self, minute_threshold=45):
        '''
        return: float - the average NO2 concentration
        This function checks if there is atleast 75% (45minutes) of no2 data of the hourly data required, then calculates the average hourly no2 concentration and returns the maximum value
        '''
        no2_grouped_by_hour = self.cachedRawData['no2'].resample('h')
        #get the hourly mean of the hours >= 45 minutes
        no2_hourlyavgs = no2_grouped_by_hour.apply(lambda x: x.mean() if x.count() >= minute_threshold else None)
        return no2_hourlyavgs
    
    def getPM2_5_24HourAvg(self, minute_threshold=1080):
        '''
        param df: pd.DataFrame
        return: float - the average PM2.5 concentration
        This function checks if there is atleast 75% (1080mins or 18hours ) of pm2.5 data of the 24hour data required, then calculates the average pm2.5 concentration
        '''
        if self.cachedRawData['pm2_5'].count() >= minute_threshold:
            return self.cachedRawData['pm2_5'].mean()
        
    def getPM10_24HourAvg(self, minute_threshold=1080):
        '''
        param df: pd.DataFrame
        return: float - the average PM10 concentration
        This function checks if there is atleast 75% (1080mins or 18hours ) of pm10 data of the 24hour data required, then calculates the average pm10 concentration
        '''
        if self.cachedRawData['pm10'].count() >= minute_threshold:
            return self.cachedRawData['pm10'].mean()
   

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
         
    def compute_aqi(self, no2_hourly_max, pm2_5_24_hour_avg, pm10_24_hour_avg):
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
        # print/("\n")
        if no2_hourly_max is None:
            aqi_data['no2'] = None
        else:
            aqi_data['no2'] = self.getNO2Index(no2_hourly_max)
            # print(f"no2 avg: {no2_hourly_avgs.max()} time: {no2_hourly_avgs.idxmax().hour}")
        if pm2_5_24_hour_avg is None:
            aqi_data['pm2_5'] = None
        else:
            # print(f"pm2.5 avg: {pm2_5_24_hour_avg}")
            aqi_data['pm2_5'] = self.getPM2_5Index(pm2_5_24_hour_avg)
        if pm10_24_hour_avg is None:
            aqi_data['pm10'] = None
        else:
            # print(f"pm10 avg: {pm10_24_hour_avg}")
            aqi_data['pm10'] = self.getPM10Index(pm10_24_hour_avg)
        # print(aqi_data)
        # print("\n")

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
                        hourly_aqis[pollutant] = list(map(self.getNO2Index, hourly_avgs[pollutant]))
                    elif pollutant == 'pm2_5':
                        hourly_aqis[pollutant] = list(map(self.getPM2_5Index, hourly_avgs[pollutant]))
                    elif pollutant == 'pm10':
                        hourly_aqis[pollutant] = list(map(self.getPM10Index, hourly_avgs[pollutant]))
            return hourly_aqis  
        


