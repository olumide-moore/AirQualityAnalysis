from django.test import SimpleTestCase
from project.services.data_processor import DataProcessor
import pandas as pd
from datetime import datetime

def average(data):
        return sum(data)/len(data)

class DataProcessorTests(SimpleTestCase):
    def setUp(self):
        self.data_processor = DataProcessor()
        self.rawdata= pd.DataFrame({
            'no2': [i//3 for i in range(1, 73)],
            'pm10': [i//3 for i in range(1, 73)],
            'pm2_5': [i//3 for i in range(1, 73)]
        }, index=pd.date_range(start='2024-01-22', periods=72, freq='20min', tz='UTC')) #rawdata for 24 hours with 3 data points per hour
        self.date = datetime.strptime('2024-01-22', '%Y-%m-%d').date()

  #extract_hrly_raw_data TESTS
    def test_extract_hrly_raw_data_valid(self):
        """Test for extract_hrly_raw_data"""
        expected = {
            'time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'],
            'no2': [[(j//3) for j in range(i, i+3)] for i in range(1, 73, 3)], #3 data points expected for each hour
            'pm10': [[(j//3) for j in range(i, i+3)] for i in range(1, 73, 3)],
            'pm2_5': [[(j//3) for j in range(i, i+3)] for i in range(1, 73, 3)]
        }
        self.assertEqual(DataProcessor.extract_hrly_raw_data(self.rawdata), expected)

    def test_extract_hrly_raw_data_empty(self):
        """Test for extract_hrly_raw_data with empty data"""
        rawdata = pd.DataFrame({
            'no2': [],
            'pm10': [],
            'pm2_5': []
        }, index=pd.date_range(start='2024-01-22', periods=0, freq='h'))
        expected = {
            'time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'],
            'no2': [[] for _ in range(24)],
            'pm10': [[] for _ in range(24)],
            'pm2_5': [[] for _ in range(24)]
        }
        self.assertEqual(DataProcessor.extract_hrly_raw_data(rawdata), expected) 

    def test_extract_hrly_raw_data_missing_pollutants(self):
        """Test for extract_hrly_raw_data with some data missing for some hours"""
        #drop data between 4th and 6th hour
        rawdata = self.rawdata.drop(self.rawdata.index[self.rawdata.index.hour.isin([4, 6])])

        expected = {
            'time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'],
            'no2': [[(j//3) for j in range(i, i+3) if i not in [(4*3)+1,(6*3)+1]] for i in range(1, 73, 3)],
            'pm10': [[(j//3) for j in range(i, i+3) if i not in [(4*3)+1,(6*3)+1]] for i in range(1, 73, 3)],
            'pm2_5': [[(j//3) for j in range(i, i+3) if i not in [(4*3)+1,(6*3)+1]] for i in range(1, 73, 3)]
        }
        self.assertEqual(DataProcessor.extract_hrly_raw_data(rawdata), expected)

    def test_extract_hrly_raw_data_missing_for_some_pollutants(self):
        """Test for extract_hrly_raw_data with some pollutants"""
        rawdata = pd.DataFrame({
            'no2': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        }, index=pd.date_range(start='2024-01-22', periods=12, freq='h'))
        expected = {
            'time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'],
            'no2': [[1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11], [12],[], [], [], [], [], [], [], [], [], [], [], []]
        }
        self.assertEqual(DataProcessor.extract_hrly_raw_data(rawdata), expected)

    def test_extract_hrly_raw_data_invalid_inputs(self):
        with self.assertRaises(ValueError):
            DataProcessor.extract_hrly_raw_data('rawdata')
        with self.assertRaises(ValueError):
            DataProcessor.extract_hrly_raw_data(pd.DataFrame({'no2': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}, index=range(10)))


  #calc_hrly_avgs_pollutants TESTS
    def test_hrly_avgs_pollutants_small_threshold(self):
        date_time= datetime.strptime('2024-01-22', '%Y-%m-%d')
        expected = {
            'time': [date_time.replace(hour=i).strftime('%Y-%m-%d %H:00:00') for i in range(24)],
            'no2': [average([(j//3) for j in range(i, i+3)]) for i in range(1, 73, 3)],
            'pm10': [average([(j//3) for j in range(i, i+3)]) for i in range(1, 73, 3)],
            'pm2_5': [average([(j//3) for j in range(i, i+3)]) for i in range(1, 73, 3)],
        }
        self.assertEqual(DataProcessor.calc_hrly_avgs_pollutants(self.rawdata, self.date, minute_threshold=1), expected)

    def test_hrly_avgs_pollutants_large_threshold(self):
        date_time= datetime.strptime('2024-01-22', '%Y-%m-%d')
        #test with at least 45 minutes of data required for the hourly average
        rawdata = pd.DataFrame({ #rawdata for 24 hours with 60 data points per hour
            'no2': [j for i in range(24) for j in range(i * 60, (i + 1) * 60)],
            'pm2_5': [j for i in range(24) for j in range(i * 60, (i + 1) * 60)],
            'pm10': [j for i in range(24) for j in range(i * 60, (i + 1) * 60)]
        }, index=pd.date_range(start=date_time, periods=24*60, freq='min', tz='UTC'))

        expected = {
            'time': [date_time.replace(hour=i).strftime('%Y-%m-%d %H:00:00') for i in range(24)],
            'no2': [average(range(i * 60, (i + 1) * 60)) for i in range(24)],
            'pm2_5': [average(range(i * 60, (i + 1) * 60)) for i in range(24)],
            'pm10': [average(range(i * 60, (i + 1) * 60)) for i in range(24)]
        }
        self.assertEqual(DataProcessor.calc_hrly_avgs_pollutants(rawdata, date_time, minute_threshold=45), expected)
    def test_hrly_avgs_pollutants_no_data(self):
        date_time= datetime.strptime('2024-01-22', '%Y-%m-%d')
        rawdata = pd.DataFrame({
            'no2': [],
            'pm10': [],
            'pm2_5': []
        }, index=pd.date_range(start='2024-01-22', periods=0, freq='h'))
        expected = {
            'time': [date_time.replace(hour=i).strftime('%Y-%m-%d %H:00:00') for i in range(24)],
            'no2': [None for _ in range(24)],
            'pm10': [None for _ in range(24)],
            'pm2_5': [None for _ in range(24)]
        }
        self.assertEqual(DataProcessor.calc_hrly_avgs_pollutants(rawdata, date_time), expected)

    def test_hrly_avgs_pollutants_insufficient_data(self):
        date_time= datetime.strptime('2024-01-22', '%Y-%m-%d')
        rawdata = pd.DataFrame({
            'no2': [i for i in range(1, 25)],
            'pm10': [i for i in range(1, 25)],
            'pm2_5': [i for i in range(1, 25)]
        }, index=pd.date_range(start='2024-01-22', periods=24, freq='h',tz='UTC'))
        rawdata = rawdata.drop(rawdata[rawdata.index.hour == 4].index) #drop the 5th hour's data for all pollutants
        expected = {
            'time': [date_time.replace(hour=i).strftime('%Y-%m-%d %H:00:00') for i in range(24)],
            'no2': [1, 2, 3, 4, None, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            'pm10': [1, 2, 3, 4, None, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            'pm2_5': [1, 2, 3, 4, None, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        }
        self.assertEqual(DataProcessor.calc_hrly_avgs_pollutants(rawdata, date_time, minute_threshold=1), expected)

    def test_hrly_avgs_pollutants_invalid_inputs(self):
        date_time= datetime.strptime('2024-01-22', '%Y-%m-%d')
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_pollutants('rawdata', date_time, minute_threshold=45)
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_pollutants(pd.DataFrame({'no2': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}, index=range(10)), date_time, minute_threshold=45)
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_pollutants(self.rawdata, 'date', minute_threshold=45)
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_pollutants(self.rawdata, datetime.strptime('1969-12-31', '%Y-%m-%d'))
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_pollutants(self.rawdata, datetime.strptime('2263-01-01', '%Y-%m-%d'))
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_pollutants(self.rawdata, date_time, minute_threshold=-1)
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_pollutants(self.rawdata, date_time, minute_threshold=61)
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_pollutants(self.rawdata, date_time, minute_threshold='45')
        

 #calc_hrly_avgs_single_pollutant TESTS
    def test_calc_hrly_avgs_single_pollutant_small_threshold(self):
        rawdata=self.rawdata['no2']
        expected = pd.Series([average([(j//3) for j in range(i, i+3)]) for i in range(1, 73, 3)], index=pd.date_range(start=self.date, periods=24, freq='h', tz='UTC'))
        self.assertTrue(DataProcessor.calc_hrly_avgs_single_pollutant(rawdata, minute_threshold=1).equals(expected))


    def test_calc_hrly_avgs_single_pollutant_large_threshold(self):
        rawdata = pd.Series([j for i in range(24) for j in range(i * 60, (i + 1) * 60)], index=pd.date_range(start=self.date, periods=24*60, freq='min', tz='UTC'))
        expected = pd.Series([average(range(i * 60, (i + 1) * 60)) for i in range(24)], index=pd.date_range(start=self.date, periods=24, freq='h', tz='UTC'))
        self.assertTrue(DataProcessor.calc_hrly_avgs_single_pollutant(rawdata, minute_threshold=45).equals(expected))

    def test_calc_hrly_avgs_single_pollutant_no_data(self):
        rawdata = pd.Series([], index=pd.date_range(start=self.date, periods=0, freq='h', tz='UTC'))
        expected = pd.Series([], index=pd.date_range(start=self.date, periods=0, freq='h', tz='UTC'))
        self.assertTrue(DataProcessor.calc_hrly_avgs_single_pollutant(rawdata).equals(expected))

    def test_calc_hrly_avgs_single_pollutant_invalid_inputs(self):
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_single_pollutant('rawdata', minute_threshold=45)
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_single_pollutant(pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], index=range(10)), minute_threshold=45)
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_single_pollutant(pd.DataFrame({'no2': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}, index=range(10)), minute_threshold=45)
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_single_pollutant(self.rawdata, minute_threshold=-1)
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_single_pollutant(self.rawdata, minute_threshold=61)
        with self.assertRaises(ValueError):
            DataProcessor.calc_hrly_avgs_single_pollutant(self.rawdata, minute_threshold='45')        


  #calc_24hr_avg_single_pollutant TESTS
    def test_calc_24hr_avg_single_pollutant_small_threshold(self):
        rawdata = self.rawdata['no2']
        expected = average([i//3 for i in range(1, 73)])
        self.assertEqual(DataProcessor.calc_24hr_avg_single_pollutant(rawdata, minute_threshold=1), expected)

    def test_calc_24hr_avg_single_pollutant_large_threshold(self):
        rawdata = pd.Series([j for i in range(24) for j in range(i * 60, (i + 1) * 60)], index=pd.date_range(start=self.date, periods=24*60, freq='min', tz='UTC'))
        expected = average(range(24*60))
        self.assertEqual(DataProcessor.calc_24hr_avg_single_pollutant(rawdata, minute_threshold=1080), expected)

    def test_calc_24hr_avg_single_pollutant_no_data(self):
        rawdata = pd.Series([], index=pd.date_range(start=self.date, periods=0, freq='h', tz='UTC'))
        self.assertIsNone(DataProcessor.calc_24hr_avg_single_pollutant(rawdata))
    
    def test_calc_24hr_avg_single_pollutant_invalid_inputs(self):
        with self.assertRaises(ValueError):
            DataProcessor.calc_24hr_avg_single_pollutant('rawdata', minute_threshold=1080)
        with self.assertRaises(ValueError):
            DataProcessor.calc_24hr_avg_single_pollutant(pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], index=range(10)), minute_threshold=1080)
        with self.assertRaises(ValueError):
            DataProcessor.calc_24hr_avg_single_pollutant(pd.DataFrame({'no2': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}, index=range(10)), minute_threshold=1080)
        with self.assertRaises(ValueError):
            DataProcessor.calc_24hr_avg_single_pollutant(self.rawdata, minute_threshold=-1)
        with self.assertRaises(ValueError):
            DataProcessor.calc_24hr_avg_single_pollutant(self.rawdata, minute_threshold=1081)
        with self.assertRaises(ValueError):
            DataProcessor.calc_24hr_avg_single_pollutant(self.rawdata, minute_threshold='1080')


  #get_correlations TESTS
    def test_get_correlations(self):
        data1 = pd.DataFrame({
            'no2': [1, 2, 3, 4, 5],
            'pm10': [6, 7, 8, 9, 10],
            'pm2_5': [11, 12, 13, 14, 15]
        }, index=pd.date_range(start='2024-01-22', periods=5, freq='h', tz='UTC'))
        data2 = pd.DataFrame({
            'no2': [6, 7, 8, 9, 10],
            'pm10': [11, 12, 13, 14, 15],
            'pm2_5': [16, 17, 18, 19, 20]
        }, index=pd.date_range(start='2024-01-22', periods=5, freq='h', tz='UTC'))
        expected = {
            'no2': 1.0,
            'pm10': 1.0,
            'pm2_5': 1.0
        }
        self.assertEqual(DataProcessor.get_correlations(data1, data2), expected)

    def test_get_correlatoins_some_nan_values(self):
        data1 = pd.DataFrame({
            'no2': [1, None, 3, 4, 5],
            'pm10': [6, 7, 8, 9, 10],
            'pm2_5': [11, 12, 13, 14, 15]
        }, index=pd.date_range(start='2024-01-22', periods=5, freq='h', tz='UTC'))
        data2 = pd.DataFrame({
            'no2': [6, 7, 8, None, 10],
            'pm10': [11, 12, 13, 14, 15],
            'pm2_5': [16, 17, 18, 19, 20]
        }, index=pd.date_range(start='2024-01-22', periods=5, freq='h', tz='UTC'))
        expected = {
            'no2': 1.0,
            'pm10': 1.0,
            'pm2_5': 1.0
        }
        self.assertEqual(DataProcessor.get_correlations(data1, data2), expected)

    def test_get_correlations_unmatched_columns(self):
        data1 = pd.DataFrame({
            'no2': [1, 2, 3, 4, 5],
            'pm10': [6, 7, 8, 9, 10],
            'pm2_5': [11, 12, 13, 14, 15]
        }, index=pd.date_range(start='2024-01-22', periods=5, freq='h', tz='UTC'))
        data2 = pd.DataFrame({
            'co2': [6, 7, 8, 9, 10],
            'pm10': [11, 12, 13, 14, 15],
            'pm2_5': [16, 17, 18, 19, 20]
        }, index=pd.date_range(start='2024-01-22', periods=5, freq='h', tz='UTC'))
        expected = {
            'no2': None,
            'co2': None,
            'pm10': 1.0,
            'pm2_5': 1.0
        }
        self.assertEqual(DataProcessor.get_correlations(data1, data2), expected)


    def test_get_correlations_empty(self):
        data1 = pd.DataFrame({
            'no2': [],
            'pm10': [],
            'pm2_5': []
        }, index=pd.date_range(start='2024-01-22', periods=0, freq='h', tz='UTC'))
        data2 = pd.DataFrame({
            'no2': [],
            'pm10': [],
            'pm2_5': []
        }, index=pd.date_range(start='2024-01-22', periods=0, freq='h', tz='UTC'))
        expected = {
            'no2': None,
            'pm10': None,
            'pm2_5': None
        }
        self.assertEqual(DataProcessor.get_correlations(data1, data2), expected)   

    def test_get_correlations_invalid_inputs(self):
        with self.assertRaises(ValueError):
            DataProcessor.get_correlations('data1', 'data2')
        with self.assertRaises(ValueError):
            DataProcessor.get_correlations(pd.Series([1, 2, 3, 4, 5], index=range(5)), pd.Series([6, 7, 8, 9, 10], index=range(5)))
        with self.assertRaises(ValueError):
            DataProcessor.get_correlations(pd.DataFrame({'no2': [1, 2, 3, 4, 5], 'pm10': [6, 7, 8, 9, 10]}, index=range(5)), pd.DataFrame({'no2': [6, 7, 8, 9, 10], 'pm10': [11, 12, 13, 14, 15]}, index=range(5)))


  #convert_df_to_dict TESTS
    def test_convert_df_to_dict(self):
        data = pd.DataFrame({
            'no2': [1, 2, 3, 4, 5],
            'pm10': [6, 7, 8, 9, 10],
            'pm2_5': [11, 12, 13, 14, 15]
        }, index=pd.date_range(start='2024-01-22', periods=5, freq='h', tz='UTC'))
        expected = {
            'time': ['2024-01-22 00:00:00', '2024-01-22 01:00:00', '2024-01-22 02:00:00', '2024-01-22 03:00:00', '2024-01-22 04:00:00'],
            'no2': [1, 2, 3, 4, 5],
            'pm10': [6, 7, 8, 9, 10],
            'pm2_5': [11, 12, 13, 14, 15]
        }
        self.assertEqual(DataProcessor.convert_df_to_dict(data), expected)

    def test_convert_df_to_dict_empty(self):
        data = pd.DataFrame({
            'no2': [],
            'pm10': [],
            'pm2_5': []
        }, index=pd.date_range(start='2024-01-22', periods=0, freq='h', tz='UTC'))
        expected = {
            'time': [],
            'no2': [],
            'pm10': [],
            'pm2_5': []
        }
        self.assertEqual(DataProcessor.convert_df_to_dict(data), expected)

    def test_convert_df_to_dict_invalid_inputs(self):
        with self.assertRaises(ValueError):
            DataProcessor.convert_df_to_dict('data')
        with self.assertRaises(ValueError):
            DataProcessor.convert_df_to_dict(pd.Series([1, 2, 3, 4, 5], index=range(5)))
        with self.assertRaises(ValueError):
            DataProcessor.convert_df_to_dict(pd.DataFrame({'no2': [1, 2, 3, 4, 5], 'pm10': [6, 7, 8, 9, 10]}, index=range(5)))