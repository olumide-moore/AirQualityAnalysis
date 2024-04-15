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
