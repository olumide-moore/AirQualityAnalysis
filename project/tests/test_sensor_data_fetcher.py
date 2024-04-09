from unittest.mock import patch, MagicMock
from django.test import TestCase
from ..services.sensor_data_fetcher import SensorDataFetcher
from ..models import *

class SensorDataFetcherTests(TestCase):
    def setUp(self):
        self.fetcher= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])
        self.fetcher.set_sensor_id(1)
        self.fetcher.set_sensor_type('Zephyr')
        return super().setUp()
    


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
        # Fetch the date and time again and check if it is returned the class field
        self.assertEqual(self.fetcher.fetch_last_updated(), "2021-01-01 12:00:00")

    # Add more tests to cover other methods and cases
