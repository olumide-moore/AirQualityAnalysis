from ..models import *
from django.db.models import DateTimeField, F 
from django.db.models.expressions import Func, Value
import pandas as pd
import numpy as np
from datetime import datetime, date

class SensorDataFetcher():
    """SensorDataFetcher fetches sensor data from the database. IT also utilizes a cache to store some previously fetched data to reduce the number of database queries"""
    def __init__(self):
        self.sensors_table = None
        self.sensor_type = None
        self.sensor_id = None
        self.last_updated = None
        self.requiredConcentrations = {
            'date_field':   'obs_date', 
            'time_field':   'obs_time_utc', 
            'no2_field':    'no2', 
            'pm10_field':   'particulatepm10',
            'pm2_5_field':  'particulatepm2_5'
            }
        self.date_field = 'obs_date'
        self.time_field = 'obs_time_utc'
        self.concentrations_fields= {'no2_field': 'no2', 'pm10_field': 'particulatepm10', 'pm2_5_field': 'particulatepm2_5'}

        self.cacheRawData = {}
        self.cacheHourlyAvgs = {}
        self.CACHE_LIMIT = 50

    def set_sensor_id(self, sensor_id : int):
        """
        Sets the sensor_id for the SensorDataFetcher object and resets the cache variables
        
        :param sensor_id: int
        """
        if not isinstance(sensor_id, int):
            raise ValueError('Invalid sensor id')
        self.sensor_id = sensor_id
        #Reset variables that depend on sensor_id
        self.last_updated = None
        self.cacheRawData = {}
        self.cacheHourlyAvgs = {}

    def get_sensor_id(self) -> int:
        return self.sensor_id

    def set_sensor_type(self, sensor_type : str):
        """
        Sets the sensor_type for the SensorDataFetcher object and changes the sensors_table based on the sensor_type

        :param sensor_type: str
        """
        if sensor_type not in [None, 'Zephyr', 'SensorCommunity', 'Plume']:
            raise ValueError('Invalid sensor type')
        self.sensor_type = sensor_type

        #if type is changed, the table also needs to be changed
        if sensor_type == 'Zephyr':
            self.sensors_table= AllSensorMeasurementsWithLocationsZephyr
        elif sensor_type == 'SensorCommunity':
            self.sensors_table= AllSensorMeasurementsWithLocationsSc
        elif sensor_type == 'Plume':
            self.sensors_table= AllPlumeMeasurements
        else:
            self.sensors_table= None

    def get_sensor_type(self) -> str:
        return self.sensor_type

    def fetch_last_updated(self) -> dict:
        """ 
        Fetches the last updated date and time for the sensor_id from the database and returns it as a dictionary
        
        :return: str - the last updated date and time (YYYY-MM-DD HH:MM:SS)
        """
        if self.sensors_table is None or self.sensor_id is None:
            return None
        if self.last_updated is not None: 
            return self.last_updated #return the last updated date if it is already fetched
        try:
            last_updated_record = self.sensors_table.objects.values(self.date_field,self.time_field).filter(sensor_id=self.sensor_id).latest(self.date_field, self.time_field)
            if last_updated_record.get(self.date_field) and last_updated_record.get(self.time_field):
                self.last_updated = f"{last_updated_record[self.date_field]} {last_updated_record[self.time_field]}"
            elif last_updated_record.get(self.date_field):
                self.last_updated = last_updated_record[self.date_field] + ' 00:00:00'
            else:
                self.last_updated = None
        except self.sensors_table.DoesNotExist:
            self.last_updated = None
        return self.last_updated
    
    def update_cache(self, rawdata : dict, hourly_avgs : dict = None):
        """
        Updates the cache with the new raw data and hourly averages while maintaining a limit on the number of days of data stored in the cache.
        If the cache hits the limit, it removes half of the data from the cache

        :param rawdata: dict - keys datetime (the date to be updated), values: pd.DataFrame (raw data for the given date
        :param hourly_avgs: (optional) dict - keys datetime (the date to be updated), values: pd.DataFrame (hourly averages for the given date
        """
        if not isinstance(rawdata, dict):
            raise ValueError('Invalid raw data')
        if not all(isinstance(k, date) and isinstance(v, pd.DataFrame) for k, v in rawdata.items()):
            raise ValueError('Invalid raw data')
        if hourly_avgs is not None:
            if not isinstance(hourly_avgs, dict):
                raise ValueError('Invalid hourly averages')
            if not all(isinstance(k, date) and isinstance(v, dict) for k, v in hourly_avgs.items()):
                raise ValueError('Invalid hourly averages')
        
        dates = list(self.cacheRawData.keys())
        #if the cache has more than 50 days of data, remove half of the data from the cache
        if len(self.cacheRawData) > self.CACHE_LIMIT:
            #remove half of the data from the cache
            for dat in dates[:len(dates)//2]: #since python 3 dictionary are ordered
                                                #so the first half of the dates will be the oldest dates
                self.cacheRawData.pop(dat, None)
                if hourly_avgs: self.cacheHourlyAvgs.pop(dat, None)
        self.cacheRawData.update(rawdata)
        if hourly_avgs: self.cacheHourlyAvgs.update(hourly_avgs)

    def fetch_raw_data(self, dates : list) -> dict:
        """ 
        Fetches the raw data from the database for the given sensor_id and the required concentrations for the given dates
        
        :param dates: list of datetime
        :return: dict - keys datetime (each date in dates), values: pd.DataFrame (raw data for the given date)
        """
        if self.sensors_table is not None and self.sensor_id is not None:
            #Fetch the raw data from database for the given sensor_id and the required concentrations for the given dates
            try:
                rawdata = (
                self.sensors_table.objects.values(self.date_field, self.time_field, *self.concentrations_fields.values())
                .filter(sensor_id=self.sensor_id)
                .annotate( 
                    datetime = ConcatDateTime(
                    F(self.date_field), 
                    Value(' '), 
                    F(self.time_field)
                    )
                ).filter(**{f"{self.date_field}__in":dates}).order_by('datetime')
                )
            except self.sensors_table.DoesNotExist:
                rawdata = {'datetime': []}
                rawdata.update({c: [] for c in self.concentrations_fields.values()})
        else:
            #If sensor table is not set, return an empty dataframe
            rawdata = {'datetime': []}
            rawdata.update({c: [] for c in self.concentrations_fields.values()})
        #Convert the queryset to a pandas dataframe
        rawdata = pd.DataFrame(rawdata, columns=['datetime', *self.concentrations_fields.values()])
        rawdata.rename(columns={self.concentrations_fields['no2_field']: 'no2', self.concentrations_fields['pm10_field']: 'pm10', self.concentrations_fields['pm2_5_field']: 'pm2_5'}, inplace=True) #rename the columns to the required names
        rawdata['datetime'] = pd.to_datetime(rawdata['datetime']) #convert the datetime column to a pandas datetime object
        rawdata.set_index('datetime', inplace=True) #set the datetime column as the index
        rawdata.replace(np.nan, None, inplace=True) #replace nan values with None
        data_by_date = {} #Store the data for each date in a dictionary
        for date in dates:
            data_by_date[date] = rawdata[rawdata.index.date == date]
        return data_by_date
    

class ConcatDateTime(Func):
    """
    This class is used to concatenate the date and time fields in the database to create a temporal datetime field in the database.
    It is a subclass of django.db.models.expressions.Func"""
    function = 'TO_TIMESTAMP'
    template = "%(function)s(CONCAT(%(expressions)s), 'YYYY-MM-DD HH24:MI:SS')"
    output_field = DateTimeField()

