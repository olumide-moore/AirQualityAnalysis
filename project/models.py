# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Logs(models.Model):
    date = models.DateTimeField(primary_key=True)
    data = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'Logs'


class Sensorsummaries(models.Model):
    timestamp = models.IntegerField(primary_key=True)  # The composite primary key (timestamp, sensor_id) found, that is not supported. The first column is selected.
    geom = models.TextField(blank=True, null=True)  # This field type is a guess.
    measurement_count = models.IntegerField()
    measurement_data = models.TextField()  # This field type is a guess.
    stationary = models.BooleanField()
    sensor = models.ForeignKey('Sensors', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'SensorSummaries'
        unique_together = (('timestamp', 'sensor'),)


class Sensortypes(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    properties = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'SensorTypes'


class Sensors(models.Model):
    lookup_id = models.CharField(max_length=50, blank=True, null=True)
    serial_number = models.CharField(unique=True, max_length=50, blank=True, null=True)
    active = models.BooleanField()
    time_created = models.DateTimeField(blank=True, null=True)
    time_updated = models.DateTimeField(blank=True, null=True)
    stationary_box = models.TextField(blank=True, null=True)  # This field type is a guess.
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    type = models.ForeignKey(Sensortypes, models.DO_NOTHING)
    active_reason = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Sensors'


class Users(models.Model):
    uid = models.CharField(primary_key=True, max_length=50)
    username = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(unique=True, max_length=50)
    role = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'Users'


class AlembicVersion(models.Model):
    version_num = models.CharField(primary_key=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'alembic_version'


class AllPlumeMeasurements(models.Model):
    sensor_id = models.IntegerField(blank=True, null=True)
    obs_date = models.DateField(blank=True, null=True)
    obs_time_utc = models.TimeField(blank=True, null=True)
    no2 = models.FloatField(db_column='NO2', blank=True, null=True)  # Field name made lowercase.
    voc = models.FloatField(db_column='VOC', blank=True, null=True)  # Field name made lowercase.
    particulatepm10 = models.FloatField(db_column='particulatePM10', blank=True, null=True)  # Field name made lowercase.
    particulatepm2_5 = models.FloatField(db_column='particulatePM2.5', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    particulatepm1 = models.FloatField(db_column='particulatePM1', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'all_plume_measurements'


class AllSensorLocations(models.Model):
    sensor_id = models.IntegerField(blank=True, null=True)
    obs_date = models.DateField(blank=True, null=True)
    obs_time_utc = models.TimeField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    no2 = models.FloatField(db_column='NO2', blank=True, null=True)  # Field name made lowercase.
    voc = models.FloatField(db_column='VOC', blank=True, null=True)  # Field name made lowercase.
    particulatepm10 = models.FloatField(db_column='particulatePM10', blank=True, null=True)  # Field name made lowercase.
    particulatepm2_5 = models.FloatField(db_column='particulatePM2.5', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    particulatepm1 = models.FloatField(db_column='particulatePM1', blank=True, null=True)  # Field name made lowercase.
    geom = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'all_sensor_locations'


class AllSensorMeasurements(models.Model):
    sensor_id = models.IntegerField(blank=True, null=True)
    obs_date = models.DateField(blank=True, null=True)
    obs_time_utc = models.TimeField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    no2 = models.FloatField(db_column='NO2', blank=True, null=True)  # Field name made lowercase.
    voc = models.FloatField(db_column='VOC', blank=True, null=True)  # Field name made lowercase.
    particulatepm10 = models.FloatField(db_column='particulatePM10', blank=True, null=True)  # Field name made lowercase.
    particulatepm2_5 = models.FloatField(db_column='particulatePM2.5', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    particulatepm1 = models.FloatField(db_column='particulatePM1', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'all_sensor_measurements'


class AllSensorMeasurementsWithLocationsPlume(models.Model):
    sensor_id = models.IntegerField(blank=True, null=True)
    obs_date = models.DateField(blank=True, null=True)
    obs_time_utc = models.TimeField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    no2 = models.FloatField(db_column='NO2', blank=True, null=True)  # Field name made lowercase.
    voc = models.FloatField(db_column='VOC', blank=True, null=True)  # Field name made lowercase.
    particulatepm10 = models.FloatField(db_column='particulatePM10', blank=True, null=True)  # Field name made lowercase.
    particulatepm2_5 = models.FloatField(db_column='particulatePM2.5', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    particulatepm1 = models.FloatField(db_column='particulatePM1', blank=True, null=True)  # Field name made lowercase.
    geom = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'all_sensor_measurements_with_locations_plume'


class AllSensorMeasurementsWithLocationsSc(models.Model):
    sensor_id = models.IntegerField(blank=True, null=True)
    obs_date = models.DateField(blank=True, null=True)
    obs_time_utc = models.TimeField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    no2 = models.FloatField(db_column='NO2', blank=True, null=True)  # Field name made lowercase.
    voc = models.FloatField(db_column='VOC', blank=True, null=True)  # Field name made lowercase.
    particulatepm10 = models.FloatField(db_column='particulatePM10', blank=True, null=True)  # Field name made lowercase.
    particulatepm2_5 = models.FloatField(db_column='particulatePM2.5', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    particulatepm1 = models.FloatField(db_column='particulatePM1', blank=True, null=True)  # Field name made lowercase.
    geom = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'all_sensor_measurements_with_locations_sc'


class AllSensorMeasurementsWithLocationsZephyr(models.Model):
    sensor_id = models.IntegerField(blank=True, null=True)
    obs_date = models.DateField(blank=True, null=True)
    obs_time_utc = models.TimeField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    no2 = models.FloatField(db_column='NO2', blank=True, null=True)  # Field name made lowercase.
    voc = models.FloatField(db_column='VOC', blank=True, null=True)  # Field name made lowercase.
    particulatepm10 = models.FloatField(db_column='particulatePM10', blank=True, null=True)  # Field name made lowercase.
    particulatepm2_5 = models.FloatField(db_column='particulatePM2.5', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    particulatepm1 = models.FloatField(db_column='particulatePM1', blank=True, null=True)  # Field name made lowercase.
    geom = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'all_sensor_measurements_with_locations_zephyr'


class SpatialRefSys(models.Model):
    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256, blank=True, null=True)
    auth_srid = models.IntegerField(blank=True, null=True)
    srtext = models.CharField(max_length=2048, blank=True, null=True)
    proj4text = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'spatial_ref_sys'
