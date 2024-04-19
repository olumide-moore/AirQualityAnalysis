from unittest.mock import patch, MagicMock
from django.test import TestCase
from ..services.sensor_data_fetcher import SensorDataFetcher
from ..models import *
from datetime import datetime, timedelta
import pandas as pd

class SensorDataFetcherTests(TestCase):
    def setUp(self):
        self.fetcher= SensorDataFetcher()
        self.fetcher.set_sensor_id(1)
        self.fetcher.set_sensor_type('Zephyr')
        return super().setUp()
    
  #set_sensor_id TESTS
    def test_set_sensor_id(self):
        
        #Test for id type
        with self.assertRaises(ValueError):
            self.fetcher.set_sensor_id('Invalid') #Test for invalid input

        with self.assertRaises(ValueError): #Test for non-integer input
            self.fetcher.set_sensor_id(1.5)

        #When the sensor id changes, the last updated and cache variables should be reset
        self.fetcher.set_sensor_id(2)
        self.assertEqual(self.fetcher.get_sensor_id(), 2)
        self.assertIsNone(self.fetcher.last_updated)
        self.assertEqual(self.fetcher.cache_rawdata, {})
        self.assertEqual(self.fetcher.cache_hourlyavgs, {})

  #set_sensor_type TESTS
    def test_set_sensor_type(self):
        #When the sensor type changes, the sensors_table should also change
        self.fetcher.set_sensor_type('Zephyr')
        self.assertEqual(self.fetcher.get_sensor_type(), 'Zephyr')
        self.assertEqual(self.fetcher.sensor_table, AllSensorMeasurementsWithLocationsZephyr)

        self.fetcher.set_sensor_type('SensorCommunity')
        self.assertEqual(self.fetcher.get_sensor_type(), 'SensorCommunity')
        self.assertEqual(self.fetcher.sensor_table, AllSensorMeasurementsWithLocationsSc)

        self.fetcher.set_sensor_type('Plume')
        self.assertEqual(self.fetcher.get_sensor_type(), 'Plume')
        self.assertEqual(self.fetcher.sensor_table, AllPlumeMeasurements)

        self.fetcher.set_sensor_type(None) #Test for None input
        self.assertIsNone(self.fetcher.sensor_table)

        with self.assertRaises(ValueError):
            self.fetcher.set_sensor_type('Invalid') #Test for invalid input
            self.assertIsNone(self.fetcher.get_sensor_type())
            self.assertIsNone(self.fetcher.sensor_table)

        with self.assertRaises(ValueError): #Test for non-string input
            self.fetcher.set_sensor_type(1)
            self.assertIsNone(self.fetcher.get_sensor_type())
            self.assertIsNone(self.fetcher.sensor_table)
        

  #fetch_last_updated TESTS
    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects')
    def test_fetch_last_updated_datetime_present(self, mock_objects):
        # Set up the mock objects for the date and time
        mock_objects.values.return_value.filter.return_value.latest.return_value = {
            'obs_date': '2021-01-01',
            'obs_time_utc': '12:00:00'
        }
        expected_datetime = "2021-01-01 12:00:00"
        self.assertEqual(self.fetcher.fetch_last_updated(), expected_datetime)

    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects')
    def test_fetch_last_updated_time_missing(self, mock_objects):
        # Set up the mock objects for valid date and missing time
        mock_objects.values.return_value.filter.return_value.latest.return_value = {
            'obs_date': '2021-01-01',
            'obs_time_utc': None
        }
        expected_datetime = "2021-01-01 00:00:00"
        self.assertEqual(self.fetcher.fetch_last_updated(), expected_datetime)

    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects')
    def test_fetch_last_updated_date_missing(self, mock_objects):
        # Set up the mock objects for missing date and valid time
        mock_objects.values.return_value.filter.return_value.latest.return_value = {
            'obs_date': None,
            'obs_time_utc': '12:00:00'
        }
        self.assertIsNone(self.fetcher.fetch_last_updated())

    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects')
    def test_fetch_last_updated_date_time_missing(self, mock_objects):
        # Set up the mock objects for missing date and time
        mock_objects.values.return_value.filter.return_value.latest.return_value = {
            'obs_date': None,
            'obs_time_utc': None
        }
        self.assertIsNone(self.fetcher.fetch_last_updated())

    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects')
    def test_fetch_last_updated_already_fetched(self, mock_objects):
        # Set up the mock objects for the date and time
        mock_objects.values.return_value.filter.return_value.latest.return_value = {
            'obs_date': '2021-01-01',
            'obs_time_utc': '12:00:00'
        }
        # Fetch the date and time
        self.fetcher.fetch_last_updated()
        self.assertEqual(self.fetcher.fetch_last_updated(), "2021-01-01 12:00:00")

    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects')
    def test_fetch_last_updated_no_sensor_table(self, mock_objects):
        # Set the sensor table to None
        self.fetcher.sensor_table = None
        self.assertIsNone(self.fetcher.fetch_last_updated())
    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects')
    def test_fetch_last_updated_no_sensor_id(self, mock_objects):
        # Set the sensor id to None
        self.fetcher.sensor_id = None
        self.assertIsNone(self.fetcher.fetch_last_updated())


 #update_cache TESTS
    def test_update_cache(self):
        #Test for valid input
        rawdata= {datetime(2021, 1, 1).date(): pd.DataFrame({'no2': [1, 2, 3], 'pm10': [4, 5, 6], 'pm2_5': [7, 8, 9]})}
        hourly_avgs= {datetime(2021, 1, 1).date(): {'time': ['00:00', '01:00', '02:00'], 'no2': [2, 3, 4], 'pm10': [5, 6, 7], 'pm2_5': [8, 9, 10]}}
        self.fetcher.update_cache(rawdata, hourly_avgs)
       
        self.assertEqual(self.fetcher.cache_rawdata, rawdata)
        self.assertEqual(self.fetcher.cache_hourlyavgs, hourly_avgs)

        pd.testing.assert_frame_equal(self.fetcher.cache_rawdata[datetime(2021, 1, 1).date()], rawdata[datetime(2021, 1, 1).date()])
        self.assertEqual(self.fetcher.cache_hourlyavgs[datetime(2021, 1, 1).date()], hourly_avgs[datetime(2021, 1, 1).date()])
    
    def test_update_cache_invalid_inputs(self):
        #Test for invalid rawdata
        with self.assertRaises(ValueError):
            rawdata= 'Invalid'
            hourly_avgs= {datetime(2021, 1, 1).date(): {'time': ['00:00', '01:00', '02:00'], 'no2': [2, 3, 4], 'pm10': [5, 6, 7], 'pm2_5': [8, 9, 10]}}
            self.fetcher.update_cache(rawdata, hourly_avgs)
        #Test for invalid hourly averages
        with self.assertRaises(ValueError):
            rawdata= {datetime(2021, 1, 1).date(): pd.DataFrame({'no2': [1, 2, 3], 'pm10': [4, 5, 6], 'pm2_5': [7, 8, 9]})}
            hourly_avgs= 'Invalid'
            self.fetcher.update_cache(rawdata, hourly_avgs)
        #Test for invalid rawdata values
        with self.assertRaises(ValueError):
            rawdata= {datetime(2021, 1, 1).date(): 'Invalid'}
            hourly_avgs= {datetime(2021, 1, 1).date(): {'time': ['00:00', '01:00', '02:00'], 'no2': [2, 3, 4], 'pm10': [5, 6, 7], 'pm2_5': [8, 9, 10]}}
            self.fetcher.update_cache(rawdata, hourly_avgs)
        #Test for invalid hourly averages values
        with self.assertRaises(ValueError):
            rawdata= {datetime(2021, 1, 1).date(): pd.DataFrame({'no2': [1, 2, 3], 'pm10': [4, 5, 6], 'pm2_5': [7, 8, 9]})}
            hourly_avgs= {datetime(2021, 1, 1).date(): 'Invalid'}
            self.fetcher.update_cache(rawdata, hourly_avgs)
        #Test for invalid rawdata key
        with self.assertRaises(ValueError):
            rawdata= {'Invalid': pd.DataFrame({'no2': [1, 2, 3], 'pm10': [4, 5, 6], 'pm2_5': [7, 8, 9]})}
            hourly_avgs= {datetime(2021, 1, 1).date(): {'time': ['00:00', '01:00', '02:00'], 'no2': [2, 3, 4], 'pm10': [5, 6, 7], 'pm2_5': [8, 9, 10]}}
            self.fetcher.update_cache(rawdata, hourly_avgs)
        #Test for invalid hourly averages key
        with self.assertRaises(ValueError):
            rawdata= {datetime(2021, 1, 1).date(): pd.DataFrame({'no2': [1, 2, 3], 'pm10': [4, 5, 6], 'pm2_5': [7, 8, 9]})}
            hourly_avgs= {'Invalid': {'time': ['00:00', '01:00', '02:00'], 'no2': [2, 3, 4], 'pm10': [5, 6, 7], 'pm2_5': [8, 9, 10]}}
            self.fetcher.update_cache(rawdata, hourly_avgs)

    def test_update_cache_cache_exceeds_limit(self):
        #Test for cache limit
        for i in range(100):
            rawdata= {datetime(2021, 1, 1).date() + timedelta(days=i): pd.DataFrame({'no2': [1, 2, 3], 'pm10': [4, 5, 6], 'pm2_5': [7, 8, 9]})}
            hourly_avgs= {datetime(2021, 1, 1).date() + timedelta(days=i): {'time': ['00:00', '01:00', '02:00'], 'no2': [2, 3, 4], 'pm10': [5, 6, 7], 'pm2_5': [8, 9, 10]}}
            self.fetcher.update_cache(rawdata, hourly_avgs)
        self.assertEqual(len(self.fetcher.cache_rawdata), 50)
        self.assertEqual(len(self.fetcher.cache_hourlyavgs), 50)
        #The first 50 days of data should be removed from the cache
        self.assertEqual(list(self.fetcher.cache_rawdata.keys()), [datetime(2021, 1, 1).date() + timedelta(days=i) for i in range(50, 100)])

 #fetch_raw_data TESTS
    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects.values')
    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects.filter')
    def test_fetch_raw_data(self, mock_filter, mock_values):
        mock_values.return_value.filter.return_value.annotate.return_value.filter.return_value.order_by.return_value = [{
            'datetime': '2021-01-01 12:00:00',
            'no2': 10.5,
            'particulatepm10': 20.5,
            'particulatepm2_5': 5.5
        }]
        expected_df = pd.DataFrame({
            'datetime': [pd.to_datetime('2021-01-01 12:00:00')],
            'no2': [10.5],
            'pm10': [20.5],
            'pm2_5': [5.5]
        }).set_index('datetime')

        data_by_date = self.fetcher.fetch_raw_data([datetime(2021, 1, 1).date()])
        pd.testing.assert_frame_equal(data_by_date[datetime(2021, 1, 1).date()], expected_df)

    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects.values')
    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects.filter')
    def test_fetch_raw_data_no_data(self, mock_filter, mock_values):
        mock_values.return_value.filter.return_value.annotate.return_value.filter.return_value.order_by.return_value = [{
        
        }]
        data_by_date = self.fetcher.fetch_raw_data([datetime(2021, 1, 1).date()])
        expected_df = pd.DataFrame(columns=['no2', 'pm10', 'pm2_5'], index=pd.DatetimeIndex([]))
        expected_df.index.name = 'datetime'
        pd.testing.assert_frame_equal(data_by_date[datetime(2021, 1, 1).date()], expected_df)

    def test_fetch_raw_data_no_sensor_table(self):
        self.fetcher.sensor_table = None
        data_by_date = self.fetcher.fetch_raw_data([datetime(2021, 1, 1).date()])
        expected_df = pd.DataFrame(columns=['no2', 'pm10', 'pm2_5'], index=pd.DatetimeIndex([]))
        expected_df.index.name = 'datetime'
        expected_df = expected_df.astype(float)
        pd.testing.assert_frame_equal(data_by_date[datetime(2021, 1, 1).date()], expected_df)

    def test_fetch_raw_data_no_sensor_id(self):
        self.fetcher.sensor_id = None
        data_by_date = self.fetcher.fetch_raw_data([datetime(2021, 1, 1).date()])
        expected_df = pd.DataFrame(columns=['no2', 'pm10', 'pm2_5'], index=pd.DatetimeIndex([]))
        expected_df.index.name = 'datetime'
        expected_df = expected_df.astype(float)
        pd.testing.assert_frame_equal(data_by_date[datetime(2021, 1, 1).date()], expected_df)

    def test_fetch_raw_data_invalid_dates(self):
        with self.assertRaises(ValueError):
            self.fetcher.fetch_raw_data('Invalid')
        with self.assertRaises(ValueError):
            self.fetcher.fetch_raw_data(['Invalid'])