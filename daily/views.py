from django.shortcuts import render
from project.views import get_sensor_ids, data_table
from django.http import HttpResponse, JsonResponse
from django.db.models import Avg, Count
from django.db.models.functions import TruncHour
from django.db.models import DateTimeField, ExpressionWrapper, F
from django.db.models.functions import Concat
from django.db.models.expressions import Func, Value
from datetime import datetime, timedelta
# import datetime


# Create your views here.
def daily(request):
    sensor_ids = get_sensor_ids()
    return render(request, 'daily.html',
                  context={'sensor_ids': sensor_ids})

def daily_sensors_data(request):
    requestGET = request.GET
    sensor_id, date= requestGET.get('sensor_id'), requestGET.get('date')
    print("daily_sensors_data")
    data=aggregate_sensor_data(date)
    return JsonResponse(
        {'data': data}
    )
class ConcatDateTime(Func):
    function = 'TO_TIMESTAMP'
    template = "%(function)s(CONCAT(%(expressions)s), 'YYYY-MM-DD HH24:MI:SS')"
    output_field = DateTimeField()

def aggregate_sensor_data(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    fields=('sensor_id', 'obs_date', 'latitude', 'longitude', 'no2', 'voc', 'particulatepm10', 'particulatepm2_5', 'particulatepm1')
    # Combine the date and time into a single datetime field
    aggregated_data = data_table.objects.values(*fields).filter(obs_date=date).annotate(
        datetime=ConcatDateTime(
            F('obs_date'), Value(' '), F('obs_time_utc')
        )
    ).annotate(
        hour_beginning=TruncHour('datetime')
    ).values(
        'hour_beginning'
    ).annotate(
        no2_count=Count('no2'),
        no2_avg=Avg('no2'),
        voc_count=Count('voc'),
        voc_avg=Avg('voc'),
        particulatepm10_count=Count('particulatepm10'),
        particulatepm10_avg=Avg('particulatepm10'),
        particulatepm2_5_count=Count('particulatepm2_5'),
        particulatepm2_5_avg=Avg('particulatepm2_5'),
        particulatepm1_count=Count('particulatepm1'),
        particulatepm1_avg=Avg('particulatepm1')

    )


    # Now aggregated_data contains the required information
    # You can render this data in your template or return as JSON

    # Example: return as JSON
    return list(aggregated_data)