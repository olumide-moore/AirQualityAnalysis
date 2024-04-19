
from ..models import Sensors, Sensortypes

def get_sensor_ids(type_id):
    '''
    Get sensor ids for a given sensor type id
    :param request: request object
    :param type_id: int - the id of the sensor type'''
    sensors = Sensors.objects.values('id').filter(type_id=type_id).order_by('id')
    sensorsids=list(map(lambda x: x['id'], sensors))
    return sensorsids

def get_all_sensor_types():
    '''
    Get sensor types from the database
    :return: dict - a dictionary of sensor types with their ids as keys and names as values'''
    sensor_types  = Sensortypes.objects.values('id','name').distinct()
    sensor_types = dict(map(lambda x: (x['id'], x['name']),sensor_types))
    return sensor_types