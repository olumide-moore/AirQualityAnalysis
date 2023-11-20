from django.shortcuts import render
from .models import AllSensorLocations, Users,AllSensorMeasurements, AllSensorMeasurementsWithLocationsZephyr
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min 
from django.db.models.functions import TruncDate

sensor_id1=None
sensor_id2=None
data_table= AllSensorMeasurementsWithLocationsZephyr
#49, 47,29, 11
def index(request):
    # fields=('sensor_id', 'obs_date', 'obs_time_utc', 'latitude', 'longitude', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1', 'geom')
    #                                                                                                     #a list is well understood json
    # all_sensor_locations = AllSensorLocations.objects.values(*fields).filter(sensor_id=sensor_id) #.values gives a query set instead of a model object
    # # print(all_sensor_locations[0]['obs_date'])
    # # print(sensors_ids())
    # # all_sensor_locations = filter_by_date('2023-01-22', all_sensor_locations)
    # # fields=('sensor_id', 'obs_date', 'obs_time_utc', 'latitude', 'longitude', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1')
    # # all_sensor_locations = AllSensorMeasurements.objects.values(*fields)[:100]
    # #Calculate mean of the data
    # mean_data = get_mean(all_sensor_locations)
    
    # context = {'all_sensor_locations': list(all_sensor_locations), 'mean_data': mean_data}
    sensor_ids = get_sensor_ids()
    return render(request, 'index.html',
                  context={'sensor_ids': sensor_ids})
    # return HttpResponse("Hello, world. You're at the project index.")

# def sensors_ids():
#     fields=('sensor_id', 'obs_date', 'obs_time_utc', 'latitude', 'longitude', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1', 'geom')
    
#     return JsonResponse(
#         {'sensors': list(AllSensorLocations.objects.values(*fields).filter(sensor_id=sensor_id))}
#     )

def get_sensor_ids():
    sensor_ids = data_table.objects.values('sensor_id').distinct()
    sensor_ids = list(map(lambda x: x['sensor_id'],sensor_ids))
    return sensor_ids
def get_mean(data):
    grouped_data = data.values('obs_date','latitude','longitude').annotate(
        no2=Avg('no2'),
        voc=Avg('voc'),
        particulatepm10=Avg('particulatepm10'),
        particulatepm2_5=Avg('particulatepm2_5'),
        particulatepm1=Avg('particulatepm1'),
    )
    # print(grouped_data)
    mean_data = {
        'no2': data.aggregate(Avg('no2'))['no2__avg'],
        'voc': data.aggregate(Avg('voc'))['voc__avg'],
        'particulatepm10': data.aggregate(Avg('particulatepm10'))['particulatepm10__avg'],
        'particulatepm2_5': data.aggregate(Avg('particulatepm2_5'))['particulatepm2_5__avg'],
        'particulatepm1': data.aggregate(Avg('particulatepm1'))['particulatepm1__avg'],
    }
    mean_data= {k: round(v, 1) if v else 0 for k, v in mean_data.items()}
    return mean_data

def sensors_data(request):
    global sensor_id1, sensor_id2
    # start_date, end_date = datetime.strptime(start_date, '%d-%b-%Y'), datetime.strptime(end_date, '%d-%b-%Y')#date format for datepicker
    # data = data_table.objects.values(*fields).filter(sensor_id=sensor_id1, obs_date__range=[start_date, end_date])
    requestGET = request.GET
    sensor_id1,sensor_id2, start_date, end_date = requestGET.get('sensor_one'),requestGET.get('sensor_two'), requestGET.get('start_date'), requestGET.get('end_date')
    data_by_date1=get_raw_data(start_date, end_date, sensor_id1)
    if sensor_id2 and sensor_id1!=sensor_id2:
        data_by_date2=get_raw_data(start_date, end_date, sensor_id2)
    else:
        data_by_date2=None
    # data_by_date = json.dumps(data_by_date, default=str)
    return JsonResponse(
        {"raw_data1":data_by_date1,
         "raw_data2":data_by_date2,}
    )

def get_raw_data(start_date, end_date, id):
    '''Returns raw data for each day within the specified date range'''
    fields=('sensor_id', 'obs_date', 'latitude', 'longitude', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1')
    start_date, end_date = datetime.strptime(start_date, '%d/%m/%Y').date(), datetime.strptime(end_date, '%d/%m/%Y').date() #date format from week range input

    # Get the raw data for each day for the sensor id
    raw_data = data_table.objects.values(*fields).filter(sensor_id=id, obs_date__range=[start_date, end_date]).order_by('obs_date', 'obs_time_utc')
    raw_data = list(raw_data)


    # Group the data by date and the no2, voc, as subdicts
    # data_by_date = {}
    data_by_date ={start_date + timedelta(days=x): {'no2': [], 'voc': [], 'particulatepm10': [], 'particulatepm2_5': [], 'particulatepm1': []} for x in range((end_date - start_date).days + 1)}

    for entry in raw_data:
        date = entry['obs_date']
        for sensor_type in ['no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1']:
            data_by_date[date][sensor_type].append(entry[sensor_type])

    data_by_date = {k.strftime('%d/%m/%Y'): v for k, v in data_by_date.items()}
    #Sort the data by date
    # data_by_date = {k.strftime('%d/%m/%Y'): v for k, v in sorted(data_by_date.items(), key=lambda item: item[0])}
    return data_by_date 
def get_avg_max_min(start_date, end_date):
    '''Returns average, max, min of the data for each day'''
    fields=('sensor_id','obs_date','latitude','longitude','no2','voc','particulatepm10','particulatepm2_5','particulatepm1')
    start_date, end_date = datetime.strptime(start_date, '%d/%m/%Y').date(), datetime.strptime(end_date, '%d/%m/%Y').date()

    #Get the data for each day for the sensor id
    data= data_table.objects.values(*fields).filter(sensor_id=sensor_id1, obs_date__range=[start_date, end_date])

    #Group the data by date and calculate mean, max, min
    grouped_data = data.values('obs_date').annotate(
        avg_no2=Avg('no2'),
        max_no2=Max('no2'),
        min_no2=Min('no2'),
        avg_voc=Avg('voc'),
        max_voc=Max('voc'),
        min_voc=Min('voc'),
        avg_particulatepm10=Avg('particulatepm10'),
        max_particulatepm10=Max('particulatepm10'),
        min_particulatepm10=Min('particulatepm10'),
        avg_particulatepm2_5=Avg('particulatepm2_5'),
        max_particulatepm2_5=Max('particulatepm2_5'),
        min_particulatepm2_5=Min('particulatepm2_5'),
        avg_particulatepm1=Avg('particulatepm1'),
        max_particulatepm1=Max('particulatepm1'),
        min_particulatepm1=Min('particulatepm1')
    )
    grouped_data = list(grouped_data)
    return grouped_data
    # list(map(lambda x:x['obs_date'].strftime("%Y-%m-%d"), grouped_data))
    
def users():
    fields=('uid','email','role','sensors','username')
    return JsonResponse(
        {'users': list(Users.objects.values(*fields))}
    )
# users = users()
# print(users)
