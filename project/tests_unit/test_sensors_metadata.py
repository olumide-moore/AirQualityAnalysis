from unittest.mock import patch, MagicMock
from django.test import TestCase
from ..services.sensors_metadata import get_sensor_ids, get_all_sensor_types
from ..models import *
from datetime import datetime, timedelta
import pandas as pd


class SensorsMetaDataTests(TestCase):
    @patch('project.models.Sensors.objects.values')
    @patch('project.models.Sensors.objects.filter')
    def test_get_sensor_ids(self, mock_filter, mock_values):
        mock_values.return_value.filter.return_value.order_by.return_value = [
            {'id': 1}, {'id': 2}]
        self.assertEqual(get_sensor_ids(1), [1, 2])

    @patch('project.models.Sensors.objects.values')
    @patch('project.models.Sensors.objects.filter')
    def test_get_sensor_ids_invalid_type(self, mock_filter, mock_values):
        mock_values.return_value.filter.return_value.order_by.return_value = []
        self.assertEqual(get_sensor_ids(1), [])

    @patch('project.models.Sensors.objects.values')
    @patch('project.models.Sensors.objects.filter')
    def test_get_sensor_ids_empty(self, mock_filter, mock_values):
        mock_values.return_value.filter.return_value.order_by.return_value = []
        self.assertEqual(get_sensor_ids(1), [])

    @patch('project.models.Sensortypes.objects.values')
    def test_get_all_sensor_types(self, mock_values):
        mock_values.return_value.distinct.return_value  = [{'id': 1, 'name': 'Plume'},
                                    {'id': 2, 'name': 'Zephyr'}]
        self.assertEqual(get_all_sensor_types(), {1: 'Plume', 2: 'Zephyr'})
    
    @patch('project.models.Sensortypes.objects.values')
    def test_get_all_sensor_types_empty(self, mock_values):
        mock_values.return_value.distinct.return_value  = []
        self.assertEqual(get_all_sensor_types(), {})
        