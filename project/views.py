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

sensor_id1=None
sensor_id2=None
# data_table= AllSensorMeasurementsWithLocationsZephyr
# data_table= AllSensorMeasurementsWithLocationsSc
data_table= AllPlumeMeasurements
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
                sensor1_data=get_daily_data(sensorids[0],date)
                sensor2_data=get_daily_data(sensorids[1],date)
            else:
                # sensorids= ['24']
                # date=pytz.timezone('UTC').localize(datetime(2024, 1, 20))
                data=get_24_hours_data_by_minute(sensorids,date)

                return JsonResponse(
                    {'data': data}
                )

            # data=get_24_hours_data_by_minute(sensorids,date)

def get_user_input(request):
    requestGET = request.GET
    sensor_one=requestGET.get('sensor_one')
    sensor_two=requestGET.get('sensor_two')
    comparing_average_trend=requestGET.get('compare_average_trend')
    date=requestGET.get('date')
    if date:    date = datetime.strptime(date, '%Y-%m-%d').date()
    start_date=requestGET.get('start_date')
    end_date=requestGET.get('end_date')
    if start_date and end_date:    start_date, end_date = datetime.strptime(start_date, '%Y-%m-%d').date(), datetime.strptime(end_date, '%Y-%m-%d').date()
           
    chart_type=requestGET.get('chart_type')
    sensorids= [sensor_one, sensor_two] if sensor_two else [sensor_one]
    data={}
    if date: 
        data=get_24_hours_data_by_minute(sensorids,date)
    for sensor_id in sensorids:
        # if date:
            # if chart_type=='Boxplot':
                # data.append(get_daily_data(sensor_id,date))
            # else:
            #     data.append(aggregate_daily_mean(sensor_id, date))
        if start_date and end_date:
            data.append(get_weekly_data(sensor_id,[start_date, end_date]))
    # data=[list(d) for d in data]
    # print(data)
    return JsonResponse(
        # {'data': data}
        data 
    )


class ConcatDateTime(Func):
    function = 'TO_TIMESTAMP'
    template = "%(function)s(CONCAT(%(expressions)s), 'YYYY-MM-DD HH24:MI:SS')"
    output_field = DateTimeField()

def get_24_hours_data_by_minute(sensor_ids,date):
    #This fetches the last 24 hours data averaged by minute
    fields=('sensor_id', 'obs_date', 'obs_time_utc', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1')
    start_datetime=date
    end_datetime = start_datetime + timezone.timedelta(days=1)
    data=[]
    for sensor_id in sensor_ids:
        #Fetch the minute average data for the last 24 hours from the database
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
            data.append({sensor_id:{'time': pd.date_range(start=start_datetime, end=end_datetime, freq='min', tz='UTC').strftime('%Y-%m-%d %H:%M:%S').tolist(),
                                    'no2':[],'voc':[],'particulatepm10':[],'particulatepm2_5':[],'particulatepm1':[]}})
            continue
        df=pd.DataFrame(data_per_minute)
        df.set_index('minute', inplace=True)
        index=pd.date_range(start=start_datetime, end=end_datetime, freq='min', tz='UTC')
        df=df.reindex(index)
        df.index=df.index.strftime('%Y-%m-%d %H:%M:%S')
        #convert nan to None
        df=df.replace(np.nan,None)
        this_data = {'time': df.index.tolist()}
        this_data.update({
            k.replace('_avg',''): df[k].values.tolist() for k in df
        })
        
        # print(df)
        data.append({sensor_id:this_data})
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

    return data

def get_daily_data(sensor_id,date):
    #This fetches the 24 hourly raw data for the specified date
    fields=('sensor_id', 'obs_date', 'obs_time_utc', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1')
    raw_data = data_table.objects.values(*fields).filter(sensor_id=sensor_id, obs_date=date).order_by('obs_date', 'obs_time_utc')
    data_by_hour = {f"{x}:00": {'no2': [], 'voc': [], 'particulatepm10': [], 'particulatepm2_5': [], 'particulatepm1': []} for x in range(24)}

    for entry in raw_data:
        hour = entry['obs_time_utc'].hour
        for sensor_type in ['no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1']:
            data_by_hour[f"{hour}:00"][sensor_type].append(entry[sensor_type])

  
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



def aggregate_daily_mean(sensor_id, date):
    fields=('sensor_id', 'obs_date', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1')
    # Combine the date and time into a single datetime field
    aggregated_data = data_table.objects.values(*fields).filter(sensor_id=sensor_id, obs_date=date).annotate(
        datetime=ConcatDateTime(
            F('obs_date'), Value(' '), F('obs_time_utc')
        )
    ).annotate(
        hour_beginning=TruncHour('datetime')
    ).values(
        'hour_beginning'
    ).annotate(
        # no2_count=Count('no2'),
        no2_avg=Avg('no2'),
        # voc_count=Count('voc'),
        voc_avg=Avg('voc'),
        # particulatepm10_count=Count('particulatepm10'),
        particulatepm10_avg=Avg('particulatepm10'),
        # particulatepm2_5_count=Count('particulatepm2_5'),
        particulatepm2_5_avg=Avg('particulatepm2_5'),
        # particulatepm1_count=Count('particulatepm1'),
        particulatepm1_avg=Avg('particulatepm1')
    )
    #Create a list of dicts for hours 1-24 with datetime objects as keys

    data_by_hour = {f"{x}:00": {'no2': None, 'voc': None, 'particulatepm10': None, 'particulatepm2_5': None, 'particulatepm1': None} for x in range(24)}
    for entry in aggregated_data:
        hour = entry['hour_beginning'].hour
        for sensor_type in ['no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1']:
            data_by_hour[f"{hour}:00"][sensor_type]=entry[f"{sensor_type}_avg"]
    
    return data_by_hour

# def get_mean(data):
#     grouped_data = data.values('obs_date','latitude','longitude').annotate(
#         no2=Avg('no2'),
#         voc=Avg('voc'),
#         particulatepm10=Avg('particulatepm10'),
#         particulatepm2_5=Avg('particulatepm2_5'),
#         particulatepm1=Avg('particulatepm1'),
#     )
#     # print(grouped_data)
#     mean_data = {
#         'no2': data.aggregate(Avg('no2'))['no2__avg'],
#         'voc': data.aggregate(Avg('voc'))['voc__avg'],
#         'particulatepm10': data.aggregate(Avg('particulatepm10'))['particulatepm10__avg'],
#         'particulatepm2_5': data.aggregate(Avg('particulatepm2_5'))['particulatepm2_5__avg'],
#         'particulatepm1': data.aggregate(Avg('particulatepm1'))['particulatepm1__avg'],
#     }
#     mean_data= {k: round(v, 1) if v else 0 for k, v in mean_data.items()}
#     return mean_data

# def weekly_sensors_data(request):
#     global sensor_id1, sensor_id2
#     # start_date, end_date = datetime.strptime(start_date, '%d-%b-%Y'), datetime.strptime(end_date, '%d-%b-%Y')#date format for datepicker
#     # data = data_table.objects.values(*fields).filter(sensor_id=sensor_id1, obs_date__range=[start_date, end_date])
#     requestGET = request.GET
#     sensor_id1,sensor_id2, start_date, end_date = requestGET.get('sensor_one'),requestGET.get('sensor_two'), requestGET.get('start_date'), requestGET.get('end_date')
#     data_by_date1=get_raw_data(start_date, end_date, sensor_id1)
#     if sensor_id2 and sensor_id1!=sensor_id2:
#         data_by_date2=get_raw_data(start_date, end_date, sensor_id2)
#     else:
#         data_by_date2=None
#     # data_by_date = json.dumps(data_by_date, default=str)
#     return JsonResponse(
#         {"raw_data1":data_by_date1,
#          "raw_data2":data_by_date2,}
    # )
# def get_raw_data(start_date, end_date, id):
#     '''Returns raw data for each day within the specified date range'''
#     fields=('sensor_id', 'obs_date', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1')
#     start_date, end_date = datetime.strptime(start_date, '%d/%m/%Y').date(), datetime.strptime(end_date, '%d/%m/%Y').date() #date format from week range input

#     # Get the raw data for each day for the sensor id
#     raw_data = data_table.objects.values(*fields).filter(sensor_id=id, obs_date__range=[start_date, end_date]).order_by('obs_date', 'obs_time_utc')
#     raw_data = list(raw_data)


#     # Group the data by date and the no2, voc, as subdicts
#     # data_by_date = {}
#     data_by_date ={start_date + timedelta(days=x): {'no2': [], 'voc': [], 'particulatepm10': [], 'particulatepm2_5': [], 'particulatepm1': []} for x in range((end_date - start_date).days + 1)}

#     for entry in raw_data:
#         date = entry['obs_date']
#         for sensor_type in ['no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1']:
#             data_by_date[date][sensor_type].append(entry[sensor_type])

#     data_by_date = {k.strftime('%d/%m/%Y'): v for k, v in data_by_date.items()}
#     #Sort the data by date
#     # data_by_date = {k.strftime('%d/%m/%Y'): v for k, v in sorted(data_by_date.items(), key=lambda item: item[0])}
#     return data_by_date 

