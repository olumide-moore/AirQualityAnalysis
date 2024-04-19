import pandas as pd
import numpy as np
from datetime import datetime, date


class DataProcessor():
    """DataProcessor class is used to process the sensor data into useful aggegates"""

    @staticmethod
    def extract_hrly_rawdata(rawdata) -> dict:
        """
        Extracts data splitted into different hours 
        
        :param rawdata: pd.DataFrame data  data for a day with a DateTimeIndex
        :return: dict  - a dictionary with time, pollutants as keys and their corresponding values
                --> {'time':['00:00','01:00',...], 'no2':[[1,2,3],[4,5,6],...], 'pm10':[[1,2,3],[4,5,6],...], 'pm2_5':[[1,2,3],[4,5,6],...]}
        """
        if not isinstance(rawdata, pd.DataFrame):
            raise ValueError("rawdata must be a pandas DataFrame")
        if not isinstance(rawdata.index, pd.DatetimeIndex):
            raise ValueError("rawdata must have a DateTimeIndex")
        
        time=[f"{t:02d}:00" for t in range(24)] #list of hours in the day in the format 'HH:00'
        data={'time': time}
        for param in ['no2', 'pm10', 'pm2_5']:
            if param in rawdata.columns:
                data[param]=[rawdata[rawdata.index.hour == t][param].tolist() for t in range(24)] #get the data for each hour (if unavailable, return an empty list for that hour)
        return data
    

    @staticmethod
    def calc_hrly_avgs_all_pollutants(rawdata, date_obj, minute_threshold=45) -> dict:
        """
        Calculates hourly averages across all given pollutants for the given date. It includes a reindexing step to include
        all hours of the day. If the number of minutes for an hour is less than the minute_threshold, None is returned for that hour.

        :param rawdata: pd.DataFrame with a DateTimeIndex
        :param date_obj: datetime.date object representing the date to calculate averages for
        :param minute_threshold: int, the minimum number of minutes required for the hourly average to be calculated
        :return: dict - a dictionary with keys for each pollutant and 'time', each containing a list of hourly averages or None
        """
        if not isinstance(rawdata, pd.DataFrame):
            raise ValueError("rawdata must be a pandas DataFrame")
        if not isinstance(rawdata.index, pd.DatetimeIndex):
            raise ValueError("rawdata must have a DateTimeIndex")
        if not isinstance(date_obj, date):
            raise ValueError("date must be a datetime.date object")
        #Check if the date isn't going to cause overflow in the conversion to ns
        if date_obj.year < 1970 or date_obj.year > 2262:
            raise ValueError("date must be between 1970 and 2262")
        if not isinstance(minute_threshold, int) or minute_threshold < 0 or minute_threshold > 60:
            raise ValueError("minute_threshold must be int between 0 and 60")

        start = datetime.combine(date_obj, datetime.min.time())  # Start of the day with time 00:00:00
        end = datetime.combine(date_obj, datetime.max.time())    # End of the day with time 23:59:59
        
        data_per_hour = rawdata.resample('h').apply( 
            lambda x: x.mean() if len(x) >= minute_threshold else np.nan)  # Resampling and calculating conditional averages
        index = pd.date_range(start=start, end=end, freq='h', tz='UTC')   # Reindex to include all hours of the day, replace missing values
        data_per_hour = data_per_hour.reindex(index)
        data_per_hour.replace(np.nan, None, inplace=True)  # Replace NaN values with None
        data_dict = DataProcessor.convert_df_to_dict(data_per_hour) #convert the dataframe to a dictionary

        return data_dict

    @staticmethod
    def calc_hrly_avgs_single_pollutant(rawdata, minute_threshold=45) -> list:
        """
        Calculates the hourly averages of the raw data with atleast [minute_threshold] minutes of data required
        
        :param rawdata: pd.Series
        :param minute_threshold: int
        :return: list - the corresponding hourly averages
        """
        if not isinstance(rawdata, pd.Series):
            raise ValueError("rawdata must be a pandas Series")
        if not isinstance(rawdata.index, pd.DatetimeIndex):
            raise ValueError("rawdata must have a DateTimeIndex")
        if not isinstance(minute_threshold, int) or minute_threshold < 0 or minute_threshold > 60:
            raise ValueError("minute_threshold must be int between 0 and 60")
        grouped_by_hour = rawdata.resample('h') #group the data by hour
        hourlyavgs = grouped_by_hour.apply(lambda x: x.mean() if x.count() >= minute_threshold else None) #calculate the average concentration for each hour if mins >= minute_threshold
        # hourlyavgs_list = hourlyavgs.tolist()
        return hourlyavgs
    
    @staticmethod
    def calc_24hr_avg_single_pollutant(rawdata, minute_threshold=1080) -> float:
        """
        Calculates the 24hour average if there is atleast [minute_threshold] minutes of data

        :param rawdata: pd.Series
        :param minute_threshold: int
        :return: float - the average concentration
        """
        if not isinstance(rawdata, pd.Series):
            raise ValueError("rawdata must be a pandas Series")
        if not isinstance(rawdata.index, pd.DatetimeIndex):
            raise ValueError("rawdata must have a DateTimeIndex")
        if not isinstance(minute_threshold, int) or minute_threshold < 0 or minute_threshold > 1440:
            raise ValueError("minute_threshold must be int between 0 and 1440")
        if rawdata.count() >= minute_threshold:
            return rawdata.mean()
        return None
    
    @staticmethod
    def calc_correlations_all_pollutants(data1, data2, resample_interval_minutes=1) -> dict:
        """
        Returns the correlations for each pollutant between two data sets using the Pearson correlation coefficient after sampling the data into the specified resolution

        :param data1: pd.DataFrame - the first data set
        :param data2: pd.DataFrame - the second data set (must have the same columns as data1)
        :param resample_interval_minutes: int - the resolution to aggregate the data to (default is 1 minute)
        :return: dict - a dictionary containing the correlation between the two data sets for each concentration
        """
        if not isinstance(data1, pd.DataFrame) or not isinstance(data2, pd.DataFrame):
            raise ValueError("data1 and data2 must be pandas DataFrames")
        if not isinstance(data1.index, pd.DatetimeIndex) or not isinstance(data2.index, pd.DatetimeIndex):
            raise ValueError("data1 and data2 must have a DateTimeIndex")
        if not isinstance(resample_interval_minutes, int) or resample_interval_minutes < 1 or resample_interval_minutes > 1440:
            raise ValueError("resample_interval_minutes must be a positive integer between 1 and 1440")
        

        correlations= {}
        #set corr for unmatched columns to None and drop the unmatched columns
        unmatched_cols= set(data1.columns) ^ set(data2.columns)
        if unmatched_cols:
            for col in unmatched_cols:
                correlations[col]= None
                if col in data1.columns:
                    data1= data1.drop(columns=col)
                if col in data2.columns:
                    data2= data2.drop(columns=col)

        if data1.empty or data2.empty: return {col : None for col in data1.columns} #if any of the data sets is empty, return None for all the attributes

        agg_data1= data1.resample(f'{resample_interval_minutes}min').mean() #resample the data to the specified resolution
        agg_data2= data2.resample(f'{resample_interval_minutes}min').mean()

        #Ensure that the two data sets have the same time indexes for the correlation calculation
        common_index= agg_data1.index.intersection(agg_data2.index)
        agg_data1= agg_data1.loc[common_index] #filter the two data to have only the common indexes
        agg_data2= agg_data2.loc[common_index]
        for conc in data1.columns: #for each column (in this case, each concentration) in the data set
            if agg_data1[conc].empty or agg_data2[conc].empty: #if any of the data sets is empty, return None for that attribute correlation
                corr= None
            else:
                corr= agg_data1[conc].corr(agg_data2[conc]) #calculate the correlation between the two data sets (Pearson correlation coefficient)
            if corr in [np.nan, None]:   #if the correlation is nan or None, return None (this happens when the data sets are nan or None)
                corr= None
            else:
                corr= round(corr, 2)
            correlations[conc]= corr
        return correlations
    
        
    
        
    @staticmethod
    def convert_df_to_dict(df):
        '''
        param df: pd.DataFrame
        return: dict - a dictionary of key- value-list pairs representing the data in the dataframe
                                        5 keys: time, no2, pm10, pm2_5, pm1
                                        and their corresponding values
        '''
        if not isinstance(df, pd.DataFrame):
            raise ValueError("df must be a pandas DataFrame")
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("df must have a DateTimeIndex")
        data_as_dict = df.to_dict(orient='list')
        data_as_dict['time'] = df.index.strftime('%Y-%m-%d %H:%M:%S').tolist() #convert the index to a list of strings
        return data_as_dict


