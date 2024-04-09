from django.test import SimpleTestCase
from project.services.aqi_calculator import AQICalculator  

#SimpleTestCase will not use the database, so it is used to test the AQI class without needing to set up a database.
class AQICalculatorTests(SimpleTestCase):
    def setUp(self):
        self.aqi_calculator = AQICalculator()


   #get_no2_index TESTS.
    def test_None_no2(self):
        """Test that None is returned when no NO2 concentration is provided."""
        self.assertIsNone(self.aqi_calculator.get_no2_index(None))    

    def test_negative_no2(self):
        """Test that negative NO2 concentrations return None."""
        self.assertIsNone(self.aqi_calculator.get_no2_index(-1))

    def test_no2_conc_zero(self):
        """Test that an NO2 concentration of 0 returns index 1."""
        self.assertEqual(self.aqi_calculator.get_no2_index(0), 1)

    def test_no2_conc_within_breakpoints(self):
        """Test NO2 concentrations that fall within each breakpoint range."""
        test_values = [1, 68, 135, 201, 268, 335, 401, 468, 535, 600]
        expected_indexes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9]
        for test_val, expected_index in zip(test_values, expected_indexes):
            # with self.\subTest(no2_conc=test_val):
                self.assertEqual(self.aqi_calculator.get_no2_index(test_val), expected_index)

    def test_no2_conc_above_range(self):
        """Test an NO2 concentration above the highest breakpoint returns the last index."""
        self.assertEqual(self.aqi_calculator.get_no2_index(601), 10)


   #get_pm2_5_index TESTS.
    def test_None_pm25(self):
        """Test that None is returned when no PM2.5 concentration is provided."""
        self.assertIsNone(self.aqi_calculator.get_pm2_5_index(None))

    def test_negative_pm25(self):
        """Test that negative PM2.5 concentrations return None."""
        self.assertIsNone(self.aqi_calculator.get_pm2_5_index(-1)) 

    def test_pm25_conc_zero(self):
        """Test that a PM2.5 concentration of 0 returns index 1."""
        self.assertEqual(self.aqi_calculator.get_pm2_5_index(0), 1)
    
    def test_pm25_conc_within_breakpoints(self):
        """Test PM2.5 concentrations that fall within each breakpoint range."""
        test_values = [1, 13, 25, 37, 45, 50, 55, 59, 66, 70]
        expected_indexes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9]
        for test_val, expected_index in zip(test_values, expected_indexes):
            self.assertEqual(self.aqi_calculator.get_pm2_5_index(test_val), expected_index)
    def test_pm25_conc_above_range(self):
        """Test a PM2.5 concentration above the highest breakpoint returns the last index."""
        self.assertEqual(self.aqi_calculator.get_pm2_5_index(501), 10)



   #get_pm10_index TESTS.
    def test_None_pm10(self):
        """Test that None is returned when no PM10 concentration is provided."""
        self.assertIsNone(self.aqi_calculator.get_pm10_index(None))

    def test_negative_pm10(self):
        """Test that negative PM10 concentrations return None."""
        self.assertIsNone(self.aqi_calculator.get_pm10_index(-1))

    def test_pm10_conc_zero(self):
        """Test that a PM10 concentration of 0 returns index 1."""
        self.assertEqual(self.aqi_calculator.get_pm10_index(0), 1)

    def test_pm10_conc_within_breakpoints(self):
        """Test PM10 concentrations that fall within each breakpoint range."""
        test_values = [1, 20, 40, 51, 66, 70, 77, 85, 96, 100]
        expected_indexes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9]
        for test_val, expected_index in zip(test_values, expected_indexes):
            # with self.\subTest(pm10_conc=test_val):
                self.assertEqual(self.aqi_calculator.get_pm10_index(test_val), expected_index)

    def test_pm10_conc_above_range(self):
        """Test a PM10 concentration above the highest breakpoint returns the last index."""
        self.assertEqual(self.aqi_calculator.get_pm10_index(181), 10)



    #compute_hourly_aqis TESTS.
    def test_compute_hourly_aqis_with_expected_data(self):
        """Test the compute_hourly_aqis method."""
        hourly_avgs = {
            'time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00'],
            'no2': [1, 68, 135, 201, 268, 335, 401, 468, 535, 601],
            'pm2_5': [1, 13, 25, 37, 45, 50, 55, 59, 66, 70],
            'pm10': [1, 16, 33, 54, 60, 67, 78, 84, 92, 101]
        }
        expected_aqis = {
            'no2': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'pm2_5': [1, 2, 3, 4, 5, 6, 7, 8, 9, 9],
            'pm10': [1, 1, 2, 4, 5, 6, 7, 8, 9, 10]
        }
        self.assertEqual(AQICalculator.compute_hourly_aqis(hourly_avgs), expected_aqis)
    def test_compute_hourly_aqis_no_data(self):
        """Test the compute_hourly_aqis method with no data."""
        hourly_avgs = {}
        expected_aqis = {'no2': [], 'pm2_5': [], 'pm10': []}
        self.assertEqual(AQICalculator.compute_hourly_aqis(hourly_avgs), expected_aqis)

    def test_compute_hourly_aqis_missing_data(self):
        """Test the compute_hourly_aqis method with missing data."""
        hourly_avgs = {
            'time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00'],
            'no2': [1, 68, 135, 201, 268, 335, 401, 468, 535],
            'pm2_5': [1, 13, 25, 37, 45, 50, 55, 59, 66],
            'pm10': [1, 16, 33, 54, 60, 67, 78, 84, 92]
        }
        expected_aqis = {
            'no2': [1, 2, 3, 4, 5, 6, 7, 8, 9, None],
            'pm2_5': [1, 2, 3, 4, 5, 6, 7, 8, 9, None],
            'pm10': [1, 1, 2, 4, 5, 6, 7, 8, 9, None]
        }
        self.assertEqual(AQICalculator.compute_hourly_aqis(hourly_avgs), expected_aqis)

    def test_compute_hourly_aqis_missing_pollutants(self):
        """Test the compute_hourly_aqis method with missing pollutants."""
        hourly_avgs = {
            'time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00'],
            'no2': [1, 68, 135, 201, 268, 335, 401, 468, 535, 601]
        }
        expected_aqis = {
            'no2': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'pm2_5': [None, None, None, None, None, None, None, None, None, None],
            'pm10': [None, None, None, None, None, None, None, None, None, None]
        }
        self.assertEqual(AQICalculator.compute_hourly_aqis(hourly_avgs), expected_aqis)
    def test_compute_hourly_aqis_missing_time(self):
        """Test the compute_hourly_aqis method with missing time."""
        hourly_avgs = {
            'no2': [5, 68, 135, 201, 268, 335, 401, 468, 535, 601],
            'pm2_5': [5, 13, 25, 37, 45, 50, 55, 59, 66, 70],
            'pm10': [5, 16, 33, 50, 58, 66, 75, 83, 91, 101]
        }
        expected_aqis = {
            'no2': [],
            'pm2_5': [],
            'pm10': []
        }
        self.assertEqual(AQICalculator.compute_hourly_aqis(hourly_avgs), expected_aqis)

    def test_compute_hourly_aqis_invalid_param(self):
        """Test the compute_hourly_aqis method with an invalid parameter."""
        self.assertIsNone(AQICalculator.compute_hourly_aqis(None))