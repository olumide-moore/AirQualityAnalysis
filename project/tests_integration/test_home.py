from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from datetime import datetime, timezone
import pandas as pd
from ..models import *

from django.contrib.auth.models import User

def average(data):
        return sum(data)/len(data)


class GetDataForDateTestCase(TestCase):
    def setUp(self):
        self.sensor_type = 'Zephyr'
        self.sensor_id = 1
        self.date = '2021-01-01'
        dates= [datetime(2021, 1, 1, 12, i, tzinfo=timezone.utc) for i in range(60)] #create utc dates
        no2s= [i for i in range(60)]
        pm2_5s= [i for i in range(60)]
        pm10s= [i for i in range(45)] + [None]*15
        self.raw_data= [
            {'datetime': d, 'no2': n, 'particulatepm2_5': p2_5, 'particulatepm10': p10} for d, n, p2_5, p10 in zip(dates, no2s, pm2_5s, pm10s)
        ]
        self.url = reverse('sensor_data_for_date', kwargs={'sensor_type': self.sensor_type, 'sensor_id': self.sensor_id, 'date': self.date})

    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects.values')
    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects.filter')    
    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects')
    def test_get_data_for_date_valid(self, mock_objects, mock_filter, mock_values):#mock_fetcher_fetch_raw_data, mock_fetcher_fetch_last_updated, mock_fetcher_instance):
        #login
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        mock_objects.values.return_value.filter.return_value.latest.return_value = {
            'obs_date': '2021-01-01',
            'obs_time_utc': '13:00:00'
        }
        mock_values.return_value.filter.return_value.annotate.return_value.filter.return_value.order_by.return_value = self.raw_data
        response = self.client.get(self.url)

        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response['last_updated'], '2021-01-01 13:00:00')
        self.assertEqual(json_response['rawdata'],{
            'time': [datetime.strptime(self.date, '%Y-%m-%d').replace(hour=12, minute=i).strftime('%Y-%m-%d %H:%M:%S') for i in range(60)],
            'no2': [i for i in range(60)],
            'pm2_5': [i for i in range(60)],
            'pm10': [i for i in range(45)] + [None]*15
        })
        self.assertEqual(json_response['hourly_avgs'], {
            'time': [datetime.strptime(self.date, '%Y-%m-%d').replace(hour=i).strftime('%Y-%m-%d %H:%M:%S') for i in range(24)],
            'no2': [29.5 if j == 12 else None for j in range(24)],
            'pm2_5': [29.5 if j == 12 else None for j in range(24)],
            'pm10': [22.0 if j == 12 else None for j in range(24)]
        })
        self.assertEqual(json_response['avg_data'], {
            'no2': 29.5,
            'pm2_5': None,
            'pm10': None
        })
        self.assertEqual(json_response['aqi_data'], {
            'no2': 1,
            'pm2_5': None,
            'pm10': None
        })

class GetHourlyAvgsAcrossDatesTestCase(TestCase):
    def setUp(self):
        self.sensor_type = 'Zephyr'
        self.sensor_id = 1
        self.dates = '2021-01-01'
        self.url = reverse('sensor_data_for_dates', kwargs={'sensor_type': self.sensor_type, 'sensor_id': self.sensor_id, 'dates': self.dates})

    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects.values')
    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects.filter')    
    def test_get_hourly_avgs_across_dates_valid_without_cached(self, mock_filter, mock_values):#mock_fetcher_fetch_raw_data, mock_fetcher_fetch_last_updated, mock_fetcher_instance):
        #login
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)

        json_response = response.json()
        # self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response['data'],{ 
             datetime.strptime('2021-01-01','%Y-%m-%d').strftime('%a, %d-%b'): {
            'time': [datetime.strptime('2021-01-01', '%Y-%m-%d').replace(hour=i).strftime('%Y-%m-%d %H:%M:%S') for i in range(24)],
            'no2': [29.5 if j == 12 else None for j in range(24)],
            'pm2_5': [29.5 if j == 12 else None for j in range(24)],
            'pm10': [22.0 if j == 12 else None for j in range(24)]
            }
        })

    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects.values')
    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects.filter')    
    def test_get_hourly_avgs_across_dates_valid_with_some_cached(self, mock_filter, mock_values):#mock_fetcher_fetch_raw_data, mock_fetcher_fetch_last_updated, mock_fetcher_instance):
        url= reverse('sensor_data_for_dates', kwargs={'sensor_type': self.sensor_type, 'sensor_id': self.sensor_id, 'dates': '2021-01-01,2021-01-02'})
        dates= [datetime(2021, 1, 2, 12, i, tzinfo=timezone.utc) for i in range(60)] #create utc dates
        no2s=  [i for i in range(60)]
        pm2_5s= [i for i in range(60)]
        pm10s= [i for i in range(45)] + [None]*15
        raw_data= [
            {'datetime': d, 'no2': n, 'particulatepm2_5': p2_5, 'particulatepm10': p10} for d, n, p2_5, p10 in zip(dates, no2s, pm2_5s, pm10s)
        ]

        #login
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        mock_values.return_value.filter.return_value.annotate.return_value.filter.return_value.order_by.return_value = raw_data
        response = self.client.get(url)

        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response['data'],{ 
             datetime.strptime('2021-01-01','%Y-%m-%d').strftime('%a, %d-%b'): {
            'time': [datetime.strptime('2021-01-01', '%Y-%m-%d').replace(hour=i).strftime('%Y-%m-%d %H:%M:%S') for i in range(24)],
            'no2': [29.5 if j == 12 else None for j in range(24)],
            'pm2_5': [29.5 if j == 12 else None for j in range(24)],
            'pm10': [22.0 if j == 12 else None for j in range(24)]
            },
                datetime.strptime('2021-01-02','%Y-%m-%d').strftime('%a, %d-%b'): {
            'time': [datetime.strptime('2021-01-02', '%Y-%m-%d').replace(hour=i).strftime('%Y-%m-%d %H:%M:%S') for i in range(24)],
            'no2': [29.5 if j == 12 else None for j in range(24)],
            'pm2_5': [29.5 if j == 12 else None for j in range(24)],
            'pm10': [22.0 if j == 12 else None for j in range(24)]
            }
        })
        