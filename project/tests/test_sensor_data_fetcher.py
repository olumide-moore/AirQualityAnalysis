from unittest.mock import patch, MagicMock
from django.test import TestCase
from ..services.sensor_data_fetcher import SensorDataFetcher
from ..models import *

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
        self.assertEqual(self.fetcher.cacheRawData, {})
        self.assertEqual(self.fetcher.cacheHourlyAvgs, {})

  #set_sensor_type TESTS
    def test_set_sensor_type(self):
        #When the sensor type changes, the sensors_table should also change
        self.fetcher.set_sensor_type('Zephyr')
        self.assertEqual(self.fetcher.get_sensor_type(), 'Zephyr')
        self.assertEqual(self.fetcher.sensors_table, AllSensorMeasurementsWithLocationsZephyr)

        self.fetcher.set_sensor_type('SensorCommunity')
        self.assertEqual(self.fetcher.get_sensor_type(), 'SensorCommunity')
        self.assertEqual(self.fetcher.sensors_table, AllSensorMeasurementsWithLocationsSc)

        self.fetcher.set_sensor_type('Plume')
        self.assertEqual(self.fetcher.get_sensor_type(), 'Plume')
        self.assertEqual(self.fetcher.sensors_table, AllPlumeMeasurements)

        self.fetcher.set_sensor_type(None) #Test for None input
        self.assertIsNone(self.fetcher.sensors_table)

        with self.assertRaises(ValueError):
            self.fetcher.set_sensor_type('Invalid') #Test for invalid input
            self.assertIsNone(self.fetcher.get_sensor_type())
            self.assertIsNone(self.fetcher.sensors_table)

        with self.assertRaises(ValueError): #Test for non-string input
            self.fetcher.set_sensor_type(1)
            self.assertIsNone(self.fetcher.get_sensor_type())
            self.assertIsNone(self.fetcher.sensors_table)
        

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
        self.fetcher.sensors_table = None
        self.assertIsNone(self.fetcher.fetch_last_updated())
    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects')
    def test_fetch_last_updated_no_sensor_id(self, mock_objects):
        # Set the sensor id to None
        self.fetcher.sensor_id = None
        self.assertIsNone(self.fetcher.fetch_last_updated())

    # # ##def update_cache(self, rawdata : dict, hourly_avgs : dict = None):
    # #     """
    # #     Updates the cache with the new raw data and hourly averages while maintaining a limit on the number of days of data stored in the cache.
    # #     If the cache hits the limit, it removes half of the data from the cache

    # #     :param rawdata: dict - keys datetime (the date to be updated), values: pd.DataFrame (raw data for the given date
    # #     :param hourly_avgs: (optional) dict - keys datetime (the date to be updated), values: pd.DataFrame (hourly averages for the given date
    # #     """
    # #     if not isinstance(rawdata, dict):
    # #         raise ValueError('Invalid raw data')
    # #     if not all(isinstance(k, datetime) and isinstance(v, pd.DataFrame) for k, v in rawdata.items()):
    # #         raise ValueError('Invalid raw data')
    # #     if hourly_avgs is not None:
    # #         if not isinstance(hourly_avgs, dict):
    # #             raise ValueError('Invalid hourly averages')
    # #         if not all(isinstance(k, datetime) and isinstance(v, pd.DataFrame) for k, v in hourly_avgs.items()):
    # #             raise ValueError('Invalid hourly averages')

    # def test_update_cache(self):
    #     #Test for valid input
    #     rawdata= {'no2': [1,2,3], 'particulatepm10': [4,5,6], 'particulatepm2_5': [7,8,9]}
    #     hourly_avgs= {'no2': 2, 'particulatepm10': 5, 'particulatepm2_5': 8}
    #     self.fetcher.update_cache(rawdata, hourly_avgs)
    #     self.assertEqual(self.fetcher.cacheRawData, rawdata)
    #     self.assertEqual(self.fetcher.cacheHourlyAvgs, hourly_avgs)

    # def test_update_cache_invalid_rawdata(self):
    #     #Test for invalid rawdata
    #     with self.assertRaises(ValueError):
    #         rawdata= 'Invalid'
    #         hourly_avgs= {'no2': 2, 'particulatepm10': 5, 'particulatepm2_5': 8}
    #         self.fetcher.update_cache(rawdata, hourly_avgs)

  