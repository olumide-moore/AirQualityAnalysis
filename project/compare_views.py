from .services import *
from django.http import JsonResponse

data_fetcher1= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])
data_fetcher2= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])

def compare_sensors_days(request, sensor_type1, sensor_id1, sensor_type2, sensor_id2, dates):
    """
    Compares the data for two sensors for the given dates.

    :param sensor_type1: str - the type of the first sensor
    :param sensor_id1: int - the id of the first sensor
    :param sensor_type2: str - the type of the second sensor
    :param sensor_id2: int - the id of the second sensor
    :param dates: str - a comma separated string of dates in the format 'YYYY-MM-DD'
    :return: JsonResponse - a json response containing the data for the given dates
    :side effect: updates the cache of the data fetcher
    """
    # ### Test data
    # date='2024-01-22'
    # sensor_type1='Zephyr'
    # sensor_id1 = 60
    # sensor_type2='Zephyr'
    # sensor_id2 = 62
    # dates='2024-01-17,2024-01-18,2024-01-19,2024-01-20,2024-01-21,2024-01-22'
    # ### End test data
    try:
        dates= dates.split(',')
        dates= [datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
    except:
        return JsonResponse(
            {'error': 'Invalid date format'}
        )
    if 'data_fetcher1' not in globals():
        global data_fetcher1
        data_fetcher1= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])
    if 'data_fetcher2' not in globals():
        global data_fetcher2
        data_fetcher2= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])

    #Check if the two the sensors is linked to data_fetcher1 or data_fetcher2, if not, link them
    if data_fetcher1.getSensorType() != sensor_type1:
        data_fetcher1.setSensorType(sensor_type1)
        data_fetcher1.setSensorId(sensor_id1)
    if data_fetcher1.getSensorId() != sensor_id1:
        data_fetcher1.setSensorId(sensor_id1)

    if data_fetcher2.getSensorType() != sensor_type2:
        data_fetcher2.setSensorType(sensor_type2)
        data_fetcher2.setSensorId(sensor_id2)
    if data_fetcher2.getSensorId() != sensor_id2:
        data_fetcher2.setSensorId(sensor_id2)
    
    sensors_data=[]
    
    for data_fetcher in [data_fetcher1, data_fetcher2]:
        dates_clone= dates.copy()
        dates_raw_data= {}
        for date in list(data_fetcher.cacheRawData.keys()):
            if date in dates_clone:
                dates_raw_data[date]= data_fetcher.cacheRawData[date]
                dates_clone.remove(date)
        if dates_clone:
            rawdata= data_fetcher.getRawData(dates_clone)
            dates_raw_data.update(rawdata)
        data_fetcher.updateCache(dates_raw_data)
        all_dates= sorted(dates_raw_data.keys(), reverse=True)
        all_dates_data= [data_fetcher.convert_df_to_dict(dates_raw_data[date]) for date in all_dates]
        all_dates= [date.strftime('%a, %d-%b') for date in all_dates]
        sensors_data.append({'dates': all_dates, 
                             'no2': [data['no2'] for data in all_dates_data], 
                             'pm2_5': [data['pm2_5'] for data in all_dates_data], 
                             'pm10': [data['pm10'] for data in all_dates_data],
                             'id': data_fetcher.getSensorId()})
    # print(sensors_data)

    
    return JsonResponse(
        {'sensor1': sensors_data[0], 'sensor2': sensors_data[1]}
    )
    

def compare_sensors_data(request, sensor_type1, sensor_id1, sensor_type2, sensor_id2, date):
    """
    Compares the data for two sensors for the given date.

    :param sensor_type1: str - the type of the first sensor
    :param sensor_id1: int - the id of the first sensor
    :param sensor_type2: str - the type of the second sensor
    :param sensor_id2: int - the id of the second sensor
    :param date: str - the date in the format 'YYYY-MM-DD'
    :return: JsonResponse - a json response containing the data for the given date
    """
    # ### Test data
    # date='2024-01-22'
    # sensor_type1='Zephyr'
    # sensor_id1 = 60
    # sensor_type2='Zephyr'
    # sensor_id2 = 62
    # ### End test data
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    except:
        return JsonResponse(
            {'error': 'Invalid date format'}
        )
    if 'data_fetcher1' not in globals():
        global data_fetcher1
        data_fetcher1= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])
    if 'data_fetcher2' not in globals():
        global data_fetcher2
        data_fetcher2= SensorDataFetcher(requiredConcentrations=['no2', 'particulatepm10', 'particulatepm2_5'])

    #Check if the two the sensors is linked to data_fetcher1 or data_fetcher2, if not, link them
    if data_fetcher1.getSensorType() != sensor_type1:
        data_fetcher1.setSensorType(sensor_type1)
        data_fetcher1.setSensorId(sensor_id1)
    if data_fetcher1.getSensorId() != sensor_id1:
        data_fetcher1.setSensorId(sensor_id1)
        
    if data_fetcher2.getSensorType() != sensor_type2:
        data_fetcher2.setSensorType(sensor_type2)
        data_fetcher2.setSensorId(sensor_id2)
    if data_fetcher2.getSensorId() != sensor_id2:
        data_fetcher2.setSensorId(sensor_id2)

    if date!=date.today() and date in data_fetcher1.cacheRawData:
        rawdata1= data_fetcher1.cacheRawData[date]
    else:
        rawdata1 = data_fetcher1.getRawData([date]).get(date)
        data_fetcher1.updateCache({date: rawdata1})
    if date!=date.today() and date in data_fetcher2.cacheRawData:
        rawdata2= data_fetcher2.cacheRawData[date]
    else:
        rawdata2 = data_fetcher2.getRawData([date]).get(date)
        data_fetcher2.updateCache({date: rawdata2})


    hourly_rawdata1= data_fetcher1.getHourlyRawData(rawdata1,date)
    hourly_rawdata2= data_fetcher2.getHourlyRawData(rawdata2,date)
    
    sensors_info= {'sensor1': {'type': data_fetcher1.getSensorType(), 'id': data_fetcher1.getSensorId(), 'last_updated': data_fetcher1.getLastUpdatedTime()},
                     'sensor2': {'type': data_fetcher2.getSensorType(), 'id': data_fetcher2.getSensorId(), 'last_updated': data_fetcher2.getLastUpdatedTime()}
                     }
    
    rawdata1_dict= data_fetcher1.convert_df_to_dict(rawdata1)
    rawdata2_dict= data_fetcher2.convert_df_to_dict(rawdata2)
    rawdata1_dict['id']= data_fetcher1.getSensorId()
    rawdata2_dict['id']= data_fetcher2.getSensorId()
    hourly_rawdata1['id']= data_fetcher1.getSensorId()
    hourly_rawdata2['id']= data_fetcher2.getSensorId()

    correlations= get_correlations(rawdata1, rawdata2)

    return JsonResponse(
        {'sensors_info': sensors_info,
            'rawdata': {'sensor1': rawdata1_dict, 'sensor2': rawdata2_dict},
            'hourly_rawdata': {'sensor1': hourly_rawdata1, 'sensor2': hourly_rawdata2},
            'correlations': correlations
        }
    )

def get_correlations(data1, data2) -> dict:
    """
    Returns the correlations for each pollutant between two data sets using the Pearson correlation coefficient after sampling the data into minute intervals.

    :param data1: list - the first data set
    :param data2: list - the second data set
    :return: dict - a dictionary containing the correlation between the two data sets for each concentration
    """
    rawdata1_minutely= data1.resample('min').mean()
    rawdata2_minutely= data2.resample('min').mean()

    #Ensure that the two data sets have the same index for the correlation calculation
    common_index= rawdata1_minutely.index.intersection(rawdata2_minutely.index)
    rawdata1_minutely= rawdata1_minutely.loc[common_index]
    rawdata2_minutely= rawdata2_minutely.loc[common_index]
    if data1.columns.to_list()!=data2.columns.to_list(): return {}
    correlation= {}
    for conc in data1.columns:
        if rawdata1_minutely[conc].empty or rawdata2_minutely[conc].empty:
            corr= None
        else:
            corr= rawdata1_minutely[conc].corr(rawdata2_minutely[conc])
        if corr in [np.nan, None]:   
            corr= None
        else:
            corr= round(corr, 2)
        correlation[conc]= corr
    return correlation
    


    