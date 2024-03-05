from typing import Any
from django.shortcuts import render
from .models import *
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min, Count, DateTimeField, ExpressionWrapper, F 
from django.db.models.functions import TruncDate, TruncHour, Concat, TruncMinute
from django.db.models.expressions import Func, Value
from django.utils import timezone
import pytz
from django.views import View
from django.db import connection
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sensor_id1=None
sensor_id2=None
data_table= AllSensorMeasurementsWithLocationsZephyr
# data_table= AllSensorMeasurementsWithLocationsSc
# data_table= AllPlumeMeasurements
#49, 47,29, 11
def index(request):
    sensor_ids = get_sensor_ids()
    return render(request, 'index.html',
                  context={'sensor_ids': sensor_ids})
def get_sensor_ids():
    sensor_ids = data_table.objects.values('sensor_id').distinct()
    sensor_ids = list(map(lambda x: x['sensor_id'],sensor_ids))
    return sensor_ids


class SensorDataView(View):
    def get(self, request):
        requestGET = request.GET
        sensor_one=requestGET.get('sensor_one')
        sensor_two=requestGET.get('sensor_two')
        comparing_average_trend=requestGET.get('compare_average_trend')
        date=requestGET.get('date')
        start_date=requestGET.get('start_date')
        end_date=requestGET.get('end_date')
        chart_type=requestGET.get('chart_type')
        if date:    date = datetime.strptime(date, '%Y-%m-%d')
        date = pytz.timezone('UTC').localize(date)
        # print(date)
        
        if start_date and end_date:    start_date, end_date = datetime.strptime(start_date, '%Y-%m-%d').date(), datetime.strptime(end_date, '%Y-%m-%d').date()

        sensorids= [sensor_one, sensor_two] if sensor_two else [sensor_one] 
        
        if date: 
            
            if comparing_average_trend==True:
                daily_average_data=get_daily_average_data(sensorids,date)
            else:
                data={}
                # sensorids= ['24','47']
                # date=pytz.timezone('UTC').localize(datetime(2024, 1, 20))
                
                if sensor_one and sensor_two and chart_type=='Bar':
                    data,correlations=get_correlation(sensorids,date)
                    return JsonResponse(
                        {'data': data, 'correlations': correlations}
                    )
                else:
                    data, correlations=get_24_hours_data_by_minute(sensorids,date)
                    # correlations=None
                    if correlations:
                        # print(data)
                        return JsonResponse(
                            {'data': data, 'correlations': correlations}
                        )
                    else:
                        return JsonResponse(
                        {'data': data}
                        )

            # data=get_24_hours_data_by_minute(sensorids,date)

class ConcatDateTime(Func):
    function = 'TO_TIMESTAMP'
    template = "%(function)s(CONCAT(%(expressions)s), 'YYYY-MM-DD HH24:MI:SS')"
    output_field = DateTimeField()

def get_correlation(sensor_ids, date):
    #This fetches the last 24 hours data averaged by minute
    start_datetime=date
    end_datetime = start_datetime + timezone.timedelta(days=1)
    data={'no2':{},'voc':{},'particulatepm10':{},'particulatepm2_5':{},'particulatepm1':{}}
    correlations={'no2':None,'voc':None,'particulatepm10':None,'particulatepm2_5':None,'particulatepm1':None}
    df1= get_minute_average_data(sensor_ids[0], start_datetime, end_datetime)
    df2= get_minute_average_data(sensor_ids[1], start_datetime, end_datetime)
    if df1 is not None and df2 is not None:
    #Calculate the difference
        for column in df1.columns:
            #rsubtract the two dataframes for each column (note: the subtraction implicitly gives NaN for missing values)
            difference = abs(df1[column] - df2[column])
            difference = difference.dropna().astype(int) #drop the nan values and convert to int
            counts=difference.value_counts().to_dict()
            data[column.replace('_avg','')]=counts
            correlation= df1[column].corr(df2[column])
            if not np.isnan(correlation):
                correlations[column.replace('_avg','')]=round(correlation, 2)

        # Plot the histogram
        # # plt.figure
        # plt.hist(difference_no2, bins=20, alpha=0.5, label='Difference in NO2')
        # plt.legend(loc='upper right')
        # plt.xlabel('Difference in NO2')
        # plt.ylabel('Frequency')
        # plt.show()
        return data, correlations
    else:
        return {},{}

def get_minute_average_data(sensor_id, start_datetime, end_datetime):
    #This fetches the minute average data for the date range from the database and returns it as a pandas dataframe
    fields=('sensor_id', 'obs_date', 'obs_time_utc', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1')
    data_per_minute = (
    data_table.objects.values(*fields)
    .filter(sensor_id=sensor_id).annotate(
        datetime=ConcatDateTime(
            F('obs_date'), Value(' '), F('obs_time_utc')
        )
    ).filter(datetime__range=[start_datetime, end_datetime])
    .annotate(minute=TruncMinute('datetime'))
    .values('minute')
    .annotate(
        no2_avg=Avg('no2'),
        voc_avg=Avg('voc'),
        particulatepm10_avg=Avg('particulatepm10'),
        particulatepm2_5_avg=Avg('particulatepm2_5'),
        particulatepm1_avg=Avg('particulatepm1')
    )
    .order_by('minute'))
    if not data_per_minute:
        return None
            
    df=pd.DataFrame(data_per_minute)
    df.set_index('minute', inplace=True)
    index=pd.date_range(start=start_datetime, end=end_datetime, freq='min', tz='UTC')
    df=df.reindex(index)
    df.index=df.index.strftime('%Y-%m-%d %H:%M:%S')
    #convert nan to None
    df=df.replace(np.nan,None)
    return df

def get_24_hours_data_by_minute(sensor_ids,date):
    #This fetches the last 24 hours data averaged by minute
    start_datetime=date
    end_datetime = start_datetime + timezone.timedelta(days=1)
    
    data=[]
    dfs=[]
    for sensor_id in sensor_ids:
        df= get_minute_average_data(sensor_id, start_datetime, end_datetime)
        dfs.append(df)
        if df is not None:
            this_data = {'time': df.index.tolist()}
            this_data.update({
                k.replace('_avg',''): df[k].values.tolist() for k in df
            })
        else:
            this_data= {'time': pd.date_range(start=start_datetime, end=end_datetime, freq='min', tz='UTC').strftime('%Y-%m-%d %H:%M:%S').tolist(),
                                        'no2':[],'voc':[],'particulatepm10':[],'particulatepm2_5':[],'particulatepm1':[]}
            
        
        # print(df)
        data.append({sensor_id:this_data})
    if len(dfs)>1:
        df1, df2 = dfs
        correlations={'no2':None,'voc':None,'particulatepm10':None,'particulatepm2_5':None,'particulatepm1':None}
        if df1 is not None and df2 is not None:
            for column in df1.columns:
                correlation= df1[column].corr(df2[column])
                if not np.isnan(correlation):
                    correlations[column.replace('_avg','')]=round(correlation, 2)
            return data, correlations

        # #Feed the data into the data template
        # for entry in data_per_minute:
        #     minute = entry['minute']
        #     for sensor_type in ['no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1']:
        #         data_template[datetime.strftime(minute, '%Y-%m-%d %H:%M:%S')][sensor_type]=entry[f"{sensor_type}_avg"]
        # data.append({sensor_id:data_template})

    # data_table.objects.raw(f"SELECT * FROM {data_table} WHERE sensor_id IN {sensor_ids} AND obs_date BETWEEN %s AND %s", [start_datetime, end_datetime])
    # cursor=connection.cursor()
    # # cursor.execute('''SELECT * FROM  all_plume_measurements LIMIT 10''')
    # cursor.execute('''SELECT * FROM %s LIMIT 2''',['all_plume_measurements'])
    # # cursor.execute('''SELECT DATE_TRUNC(minute, TO_TIMESTAMP(CONCAT(obs_date, ' ' , obs_time_utc), 'YYYY-MM-DD HH24:MI:SS') AT TIME ZONE UTC) AS minute,
    # #                 AVG(NO2) AS no2_avg, AVG(VOC) AS voc_avg, AVG(particulatePM10) AS particulatepm10_avg, AVG(particulatePM2.5) AS particulatepm2_5_avg, AVG(particulatePM1) AS particulatepm1_avg FROM all_plume_measurements 
    # #                WHERE (sensor_id = 24 AND TO_TIMESTAMP(CONCAT(obs_date,  , obs_time_utc), 'YYYY-MM-DD HH24:MI:SS') BETWEEN 2024-01-20 00:00:00+00:00 AND 2024-01-21 00:00:00+00:00) GROUP BY 1 ORDER BY 1 ASC''',
    # #                [])
    # cursor.fetchall()
    # cursor.close()
    # cursor.execute(f"SELECT * FROM {data_table} WHERE sensor_id IN {sensor_ids} AND obs_date BETWEEN %s AND %s", [start_datetime, end_datetime])

    return data, None

    return data_by_hour
def get_weekly_data(sensor_id,date):
    fields=('sensor_id', 'obs_date', 'obs_time_utc', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1')
    start_date, end_date = date[0], date[1]
    raw_data = data_table.objects.values(*fields).filter(sensor_id=sensor_id, obs_date__range=[start_date, end_date])
    data_by_date ={start_date + timedelta(days=x): {'no2': [], 'voc': [], 'particulatepm10': [], 'particulatepm2_5': [], 'particulatepm1': []} for x in range((end_date - start_date).days + 1)}

    for entry in raw_data:
        date = entry['obs_date']
        for sensor_type in ['no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1']:
            data_by_date[date][sensor_type].append(entry[sensor_type])

    data = {k.strftime('%d/%m/%Y'): v for k, v in data_by_date.items()}
    return data




# def get_user_input(request):
#     requestGET = request.GET
#     sensor_one=requestGET.get('sensor_one')
#     sensor_two=requestGET.get('sensor_two')
#     comparing_average_trend=requestGET.get('compare_average_trend')
#     date=requestGET.get('date')
#     if date:    date = datetime.strptime(date, '%Y-%m-%d').date()
#     start_date=requestGET.get('start_date')
#     end_date=requestGET.get('end_date')
#     if start_date and end_date:    start_date, end_date = datetime.strptime(start_date, '%Y-%m-%d').date(), datetime.strptime(end_date, '%Y-%m-%d').date()
           
#     chart_type=requestGET.get('chart_type')
#     sensorids= [sensor_one, sensor_two] if sensor_two else [sensor_one]
#     data={}
#     if date: 
#         data=get_24_hours_data_by_minute(sensorids,date)
#     for sensor_id in sensorids:
        
#         if start_date and end_date:
#             data.append(get_weekly_data(sensor_id,[start_date, end_date]))
#     # data=[list(d) for d in data]
#     # print(data)
#     return JsonResponse(
#         # {'data': data}
#         data 
#     )


