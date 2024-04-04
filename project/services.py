from .models import *

from django.db.models import Avg, DateTimeField, F 
from django.db.models.expressions import Func, Value

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class SensorDataFetcher():
    def __init__(self, requiredConcentrations):
        self.sensors_table = None
        self.sensor_type = None
        self.sensor_id = None
        self.last_updated = None
        self.requiredConcentrations = requiredConcentrations

        self.cacheRawData = {}
        self.cacheHourlyAvgs = {}

    def setSensorId(self, sensor_id):
        """
        Sets the sensor_id for the SensorDataFetcher object and resets the cache variables
        
        :param sensor_id: int"""
        self.sensor_id = sensor_id
        #Reset variables that depend on sensor_id
        self.last_updated = None
        self.cacheRawData = {}
        self.cacheHourlyAvgs = {}

    def getSensorId(self) -> int:
        return self.sensor_id

    def setSensorType(self, sensor_type):
        self.sensor_type = sensor_type
        self.setSensorsTable(sensor_type) #if type is changed, the table also needs to be changed

    def getSensorType(self) -> str:
        return self.sensor_type

    def setSensorsTable(self, sensor_type):
        """
        Sets the sensors_table based on the sensor_type

        :param sensor_type: str
        """
        if sensor_type == 'Zephyr':
            self.sensors_table= AllSensorMeasurementsWithLocationsZephyr
        elif sensor_type == 'SensorCommunity':
            self.sensors_table= AllSensorMeasurementsWithLocationsSc
        elif sensor_type == 'Plume':
            self.sensors_table= AllPlumeMeasurements
        else:
            self.sensors_table= None

    def getLastUpdatedTime(self) -> dict:
        """ 
        Fetches the last updated date and time for the sensor_id from the database and returns it as a dictionary
        
        :return: dict --> {'obs_date': datetime.date, 'obs_time_utc': datetime.time}
        """

        if self.sensors_table is None: return None
        if self.last_updated is not None: return self.last_updated
        try:
            last_updated = self.sensors_table.objects.values('obs_date','obs_time_utc').filter(sensor_id=self.sensor_id).latest('obs_date', 'obs_time_utc')
        except self.sensors_table.DoesNotExist:
            last_updated = None
        self.last_updated = last_updated
        return last_updated
    
    def updateCache(self, rawdata, hourly_avgs=None):
        """
        Updates the cache with the new raw data and hourly averages and maintains only 50 days of data in the cache
        
        :param rawdata: pd.DataFrame
        :param hourly_avgs: pd.DataFrame
        """
        dates = list(self.cacheRawData.keys())
        #if the cache has more than 50 days of data, reset the cache
        if len(self.cacheRawData) > 50:
            #remove half of the data from the cache
            for date in dates[:len(dates)//2]:
                self.cacheRawData.pop(date, None)
                if hourly_avgs: self.cacheHourlyAvgs.pop(date, None)
        self.cacheRawData.update(rawdata)
        if hourly_avgs: self.cacheHourlyAvgs.update(hourly_avgs)

    def getRawData(self, dates) -> dict:
        """ 
        Fetches the raw data from the database for the given sensor_id and the required concentrations for the given dates
        
        :param dates: list of datetime
        :return: dict keys: datetime (each date in dates), values: pd.DataFrame (raw data for the given date)
        """
        if self.sensors_table:
            #Fetch the raw data from database for the given sensor_id and the required concentrations for the given dates
            try:
                rawdata = (
                self.sensors_table.objects.values('obs_date', 'obs_time_utc', *self.requiredConcentrations)
                .filter(sensor_id=self.sensor_id)
                .annotate( 
                    datetime = ConcatDateTime(
                    F('obs_date'), 
                    Value(' '), 
                    F('obs_time_utc')
                    )
                ).filter(obs_date__in=dates).order_by('datetime')
                )
            except self.sensors_table.DoesNotExist:
                rawdata = {'datetime': []}
                rawdata.update({c: [] for c in self.requiredConcentrations})
        else:
            #If sensor table is not set, return an empty dataframe
            rawdata = {'datetime': []}
            rawdata.update({c: [] for c in self.requiredConcentrations})
        #Convert the queryset to a pandas dataframe
        rawdata = pd.DataFrame(rawdata, columns=['datetime', *self.requiredConcentrations]) #convert the queryset to a pandas dataframe
        rawdata.rename(columns={'particulatepm2_5':'pm2_5', 'particulatepm10':'pm10', 'particulatepm1':'pm1'}, inplace=True) #Rename the columns
        rawdata['datetime'] = pd.to_datetime(rawdata['datetime']) #convert the datetime column to a pandas datetime object
        rawdata.set_index('datetime', inplace=True) #set the datetime column as the index
        rawdata.replace(np.nan, None, inplace=True) #replace nan values with None
        data_by_date = {} #Store the data for each date in a dictionary
        for date in dates:
            data_by_date[date] = rawdata[rawdata.index.date == date]
        return data_by_date
    
    def getHourlyRawData(self,rawdata, date) -> dict:
        """
        Fetches the hourly raw data from the database for the given sensor_id and the required concentrations for the given date
        
        :param date: datetime
        :return: dict  - a dictionary of key- value-list pairs representing the hourly raw data for each pollutants and the time
                           --> 4 keys: time, no2, pm10, pm2_5 and their corresponding 24 values
        """
        start= datetime.combine(date, datetime.min.time()) #start of the day
        end= datetime.combine(date, datetime.max.time())
        time=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        data={'time': list(map(lambda t: f"{t}".zfill(0)+":00", time))}
        for param in ['no2', 'pm10', 'pm2_5']:
            data[param]=[]
        for t in time:
            cur_hour_data=rawdata[rawdata.index.hour == t].to_dict(orient='list')
            for param in ['no2', 'pm10', 'pm2_5']:
                data[param].append(cur_hour_data[param])
        return data
            
    def getHourlyAverages(self, rawdata, date, minute_threshold=45) -> dict:
        """
        Calculates the average concentration of the pollutants for each hour between the start and end datetime.
        
        :param rawdata: pd.DataFrame
        :param date: datetime
        :return: dict - a dictionary of key- value-list pairs representing the hourly averages for each pollutants and the time
        """
        start = datetime.combine(date, datetime.min.time()) #start of the day
        end = datetime.combine(date, datetime.max.time())   #end of the day
        index=pd.date_range(start=start, end=end, freq='h', tz='UTC')
        #group the data by hour and calculate the average concentration for each hour
        data_grouped_by_hour = rawdata.resample('h')
        data_per_hour = data_grouped_by_hour.apply(lambda x: x.mean() if x.count() >= minute_threshold else None)
        #insert missing hours with None values
        data_per_hour = data_per_hour.reindex(index)
        data_per_hour.replace(np.nan, None, inplace=True)
        data_per_hour = self.convert_df_to_dict(data_per_hour)
        return data_per_hour 
           
    def convert_df_to_dict(self,df):
        '''
        param df: pd.DataFrame
        return: dict - a dictionary of key- value-list pairs representing the data in the dataframe
                                        5 keys: time, no2, pm10, pm2_5, pm1
                                        and their corresponding values
        '''
        data_as_dict = df.to_dict(orient='list')
        data_as_dict['time'] = df.index.strftime('%Y-%m-%d %H:%M:%S').tolist() #convert the index to a list of strings
        return data_as_dict

    def getNO2_HourlyAvgs(self, no2_rawdata, minute_threshold=45) -> pd.Series:
        """
        Checks if there is atleast 75% (45minutes) of no2 data of the hourly data required, then calculates the average hourly no2 concentration and returns the maximum value
        
        :param no2_rawdata: pd.Series
        :param minute_threshold: int
        :return: float - the average NO2 concentration
        """
        no2_grouped_by_hour = no2_rawdata.resample('h')
        #get the hourly mean of the hours >= 45 minutes
        no2_hourlyavgs = no2_grouped_by_hour.apply(lambda x: x.mean() if x.count() >= minute_threshold else None)
        return no2_hourlyavgs
    
    def getPM2_5_24HourAvg(self, pm2_5_rawdata, minute_threshold=1080) -> float:
        """
        Checks if there is atleast 75% (1080mins or 18hours ) of pm2.5 data of the 24hour data required, then calculates the average pm2.5 concentration

        :param pm2_5_rawdata: pd.Series
        :param minute_threshold: int
        :return: float - the average PM2.5 concentration
        """
        if pm2_5_rawdata.count() >= minute_threshold:
            return pm2_5_rawdata.mean()
        
    def getPM10_24HourAvg(self, pm10_rawdata, minute_threshold=1080) -> float:
        """
        Checks if there is atleast 75% (1080mins or 18hours ) of pm10 data of the 24hour data required, then calculates the average pm10 concentration

        :param pm10_rawdata: pd.Series
        :param minute_threshold: int
        :return: float - the average PM10 concentration
        """
        if pm10_rawdata.count() >= minute_threshold:
            return pm10_rawdata.mean()
   

class ConcatDateTime(Func):
    """
    This class is used to concatenate the date and time fields in the database to create a temporal datetime field in the database.
    It is a subclass of django.db.models.expressions.Func"""
    function = 'TO_TIMESTAMP'
    template = "%(function)s(CONCAT(%(expressions)s), 'YYYY-MM-DD HH24:MI:SS')"
    output_field = DateTimeField()


class AQI:
    def __init__(self):
        self.NO2_BREAKPOINTS = [67, 134, 200, 267, 334, 400, 467, 534, 600]
        self.PM2_5_BREAKPOINTS = [11, 23, 35, 41, 47, 53, 58, 64, 70]
        self.PM10_BREAKPOINTS = [16, 33, 50, 58, 66, 75, 83, 91, 100]
    
    def getNO2Index(self, no2_avg) -> int:
        """
        Get the AQI value for NO2 based on the average concentration

        :param no2_avg: float
        :return: int - the AQI value
        """
        if no2_avg == None or no2_avg < 0: return None
        for index, breakpoint in enumerate(self.NO2_BREAKPOINTS):
            if no2_avg <= breakpoint:
                return index+1
        return 10
    
    def getPM2_5Index(self, pm2_5_avg) -> int:
        """
        Get the AQI value for PM2.5 based on the average concentration

        :param pm2_5_avg: float
        :return: int - the AQI value
        """
        if pm2_5_avg == None or pm2_5_avg < 0: return None
        for index, breakpoint in enumerate(self.PM2_5_BREAKPOINTS):
            if pm2_5_avg <= breakpoint:
                return index+1
        return 10
    
    def getPM10Index(self, pm10_avg) -> int:
        """
        Get the AQI value for PM10 based on the average concentration

        :param pm10_avg: float
        :return: int - the AQI value
        """
        if pm10_avg == None or pm10_avg < 0: return None
        for index, breakpoint in enumerate(self.PM10_BREAKPOINTS):
            if pm10_avg <= breakpoint:
                return index+1
        return 10
         
    def compute_hourly_aqis(self, hourly_avgs) -> dict:
        """
        Computes the hourly AQI values for the 3 pollutants
        The AQI values and their corresponding categories are then returned as a dictionary
        
        :param hourly_avgs: dict
        :return: dict - a dictionary of key- value pairs representing the hourly AQI values for the 3 pollutants
        """
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
        


