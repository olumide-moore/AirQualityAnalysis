class AQICalculator():
    NO2_BREAKPOINTS = [67, 134, 200, 267, 334, 400, 467, 534, 600]
    PM2_5_BREAKPOINTS = [11, 23, 35, 41, 47, 53, 58, 64, 70]
    PM10_BREAKPOINTS = [16, 33, 50, 58, 66, 75, 83, 91, 100]

    @staticmethod
    def _get_index(avg : float, breakpoints: list) -> int:
        """
        Helper method to get the AQI index based on the average concentration and the breakpoints
        
        :param avg: float - the average concentration
        :param breakpoints: list - the breakpoints for the pollutant
        :return: int - the AQI index
        """
        if avg is None or avg < 0:
            return None
        for index, breakpoint in enumerate(breakpoints):
            if avg <= breakpoint:
                return index + 1
        return 10

    @staticmethod
    def get_no2_index(no2_avg : float) -> int:
        """
        Get the AQI value for NO2 based on the average concentration
        
        :param no2_avg: float
        :return: int - the AQI value"""
        return AQICalculator._get_index(no2_avg, AQICalculator.NO2_BREAKPOINTS)

    @staticmethod
    def get_pm2_5_index(pm2_5_avg :float) -> int:
        """
        Get the AQI value for PM2.5 based on the average concentration
        
        :param pm2_5_avg: float
        :return: int - the AQI value"""
        return AQICalculator._get_index(pm2_5_avg, AQICalculator.PM2_5_BREAKPOINTS)
    

    @staticmethod
    def get_pm10_index(pm10_avg : float) -> int:
        """
        Get the AQI value for PM10 based on the average concentration
        
        :param pm10_avg: float
        :return: int - the AQI value"""
        return AQICalculator._get_index(pm10_avg, AQICalculator.PM10_BREAKPOINTS)

    @staticmethod
    def compute_hourly_aqis(hourly_avgs : dict) -> dict:
        """
        Computes the hourly AQI values for the 3 pollutants
        The AQI values and their corresponding categories are then returned as a dictionary
        
        :param hourly_avgs: dict - a dictionary of key- value pairs consisting of the time span and the hourly averages for the pollutants -> {'time': [time1, time2, ...], 'no2': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 'pm2_5': [...], 'pm10': [...]}
        :return: dict - a dictionary of key- value pairs representing the hourly AQI values for the 3 pollutants
                --> {'no2': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 'pm2_5': [...], 'pm10': [...]}
        """
        if type(hourly_avgs) is not dict: return None
        hourly_aqis = {}
        for pollutant in ['no2', 'pm2_5', 'pm10']:
            cur_pollutant_aqis = [None] * len(hourly_avgs.get('time', [])) #initialize the list with None values as each hour's AQI value
            if pollutant in hourly_avgs:
                for i, avg in enumerate(hourly_avgs[pollutant]): #iterate through the hourly averages for the pollutant
                    if len(cur_pollutant_aqis) > i: #if the index is within the range of the list (i.e. the time span is not over)
                        cur_pollutant_aqis[i] = AQICalculator._get_index(avg, getattr(AQICalculator, f"{pollutant.upper()}_BREAKPOINTS")) #get the AQI index for the average concentration
            hourly_aqis[pollutant] = cur_pollutant_aqis #store the AQI values for the pollutant in the dictionary
        return hourly_aqis
    

