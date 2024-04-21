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
        self.date = '2021-01-01'
        dates= [datetime(2021, 1, 1, 12, i, tzinfo=timezone.utc) for i in range(60)] #create utc dates
        no2s= [i for i in range(60)]
        pm2_5s= [i for i in range(60)]
        pm10s= [i for i in range(45)] + [None]*15
        self.raw_data= [
            {'datetime': d, 'no2': n, 'particulatepm2_5': p2_5, 'particulatepm10': p10} for d, n, p2_5, p10 in zip(dates, no2s, pm2_5s, pm10s)
        ]
        self.url = reverse('sensors_data_for_date', kwargs={'sensor_type1': self.sensor_type, 'sensor_id1': 1, 'sensor_type2': self.sensor_type, 'sensor_id2': 2, 'date': self.date, 'corravginterval': 1})

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
    
        self.assertEqual(json_response['sensors_info'],{
            'sensor1': {'type': 'Zephyr', 'id': 1, 'last_updated': '2021-01-01 13:00:00'},
            'sensor2': {'type': 'Zephyr', 'id': 2, 'last_updated': '2021-01-01 13:00:00'}
        })
        self.assertEqual(json_response['hourly_rawdata'],{
             'sensor1': {
            'time': [f"{i}".zfill(2)+":00" for i in range(24)],
            'no2': [[] if j != 12 else [i for i in range(60)] for j in range(24)],
            'pm2_5': [[] if j != 12 else [i for i in range(60)] for j in range(24)],
            'pm10': [[] if j != 12 else [float(i) for i in range(45)] + [None]*15 for j in range(24)],
            'id': 1
            },
            'sensor2': {
            'time': [f"{i}".zfill(2)+":00" for i in range(24)],
            'no2': [[] if j != 12 else [i for i in range(60)] for j in range(24)],
            'pm2_5': [[] if j != 12 else [i for i in range(60)] for j in range(24)],
            'pm10': [[] if j != 12 else [float(i) for i in range(45)] + [None]*15 for j in range(24)],
            'id': 2
            }
        })
        self.assertEqual(json_response['rawdata'], {
             'sensor1': {
                  'time': [datetime.strptime(self.date, '%Y-%m-%d').replace(hour=12, minute=i).strftime('%Y-%m-%d %H:%M:%S') for i in range(60)],
                    'no2': [i for i in range(60)],
                    'pm2_5': [i for i in range(60)],
                    'pm10': [i for i in range(45)] + [None]*15,
                    'id': 1
                },
                'sensor2': {
                  'time': [datetime.strptime(self.date, '%Y-%m-%d').replace(hour=12, minute=i).strftime('%Y-%m-%d %H:%M:%S') for i in range(60)],
                    'no2': [i for i in range(60)],
                    'pm2_5': [i for i in range(60)],
                    'pm10': [i for i in range(45)] + [None]*15,
                    'id': 2
                }
        })
        self.assertEqual(json_response['correlations'], {
             'no2': 1.0, 'pm2_5': 1.0, 'pm10': 1.0
             })
             
        self.assertEqual(response.status_code, 200)

class UpdateCorrelations(TestCase):
    def setUp(self):
        self.sensor_type = 'Zephyr'
        self.date = '2021-01-01'


        self.url = reverse('updateCorrelation', kwargs={'sensor_type1': self.sensor_type, 'sensor_id1': 1, 'sensor_type2': self.sensor_type, 'sensor_id2': 2, 'date': self.date, 'corravginterval': 1})

    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects.values')
    @patch('project.models.AllSensorMeasurementsWithLocationsZephyr.objects.filter')    
    def test_get_data_for_date_valid(self,  mock_filter, mock_values):#mock_fetcher_fetch_raw_data, mock_fetcher_fetch_last_updated, mock_fetcher_instance):
        #login
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(self.url)

        json_response = response.json()
 
        self.assertEqual(json_response['correlations'], {
             'no2': 1.0, 'pm2_5': 1.0, 'pm10': 1.0
             })
             
        self.assertEqual(response.status_code, 200)