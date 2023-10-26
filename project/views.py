from django.shortcuts import render
from .models import AllSensorLocations, Users,AllSensorMeasurements
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from django.db.models import Avg

sensor_id=11
#49, 47,29, 11
def index(request):
    fields=('sensor_id', 'obs_date', 'obs_time_utc', 'latitude', 'longitude', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1', 'geom')
                                                                                                        #a list is well understood json
    all_sensor_locations = AllSensorLocations.objects.values(*fields).filter(sensor_id=sensor_id) #.values gives a query set instead of a model object
    # print(all_sensor_locations[0]['obs_date'])
    # print(sensors_ids())
    # all_sensor_locations = filter_by_date('2023-01-22', all_sensor_locations)
    # fields=('sensor_id', 'obs_date', 'obs_time_utc', 'latitude', 'longitude', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1')
    # all_sensor_locations = AllSensorMeasurements.objects.values(*fields)[:100]
    #Calculate mean of the data
    mean_data = get_mean(all_sensor_locations)
    
    context = {'all_sensor_locations': list(all_sensor_locations), 'mean_data': mean_data}
    return render(request, 'index.html', context)
    # return HttpResponse("Hello, world. You're at the project index.")

# def sensors_ids():
#     fields=('sensor_id', 'obs_date', 'obs_time_utc', 'latitude', 'longitude', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1', 'geom')
    
#     return JsonResponse(
#         {'sensors': list(AllSensorLocations.objects.values(*fields).filter(sensor_id=sensor_id))}
#     )

def get_mean(all_sensor_locations):
    mean_data = {
        'no2': all_sensor_locations.aggregate(Avg('no2'))['no2__avg'],
        'voc': all_sensor_locations.aggregate(Avg('voc'))['voc__avg'],
        'particulatepm10': all_sensor_locations.aggregate(Avg('particulatepm10'))['particulatepm10__avg'],
        'particulatepm2_5': all_sensor_locations.aggregate(Avg('particulatepm2_5'))['particulatepm2_5__avg'],
        'particulatepm1': all_sensor_locations.aggregate(Avg('particulatepm1'))['particulatepm1__avg'],
    }
    mean_data= {k: round(v, 1) if v else 0 for k, v in mean_data.items()}
    return mean_data

def sensors_data(request):
    start_date, end_date = request.GET.get('start_date'), request.GET.get('end_date')
    start_date, end_date = datetime.strptime(start_date, '%d-%b-%Y'), datetime.strptime(end_date, '%d-%b-%Y')
    fields=('sensor_id', 'obs_date', 'obs_time_utc', 'latitude', 'longitude', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1', 'geom')
    all_sensor_locations = AllSensorLocations.objects.values(*fields).filter(sensor_id=sensor_id, obs_date__range=[start_date, end_date])
    return JsonResponse(
        {'sensors': list(all_sensor_locations), 'mean': get_mean(all_sensor_locations)}
    )

def users():
    fields=('uid','email','role','sensors','username')
    return JsonResponse(
        {'users': list(Users.objects.values(*fields))}
    )
# users = users()
# print(users)

# def get_mean(all_sensor_locations):
