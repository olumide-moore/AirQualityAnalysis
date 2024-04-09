class AirQualityRouter:
    """
    A router to control all database operations on models in the
    application for air quality data.
    """

    route_app_labels = {'project'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read air quality models go to airqualitydb.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'airqualitydb'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Writes always go to the default database.
        We don't want to write to the air quality database.
        """
        return 'default' #Direct all writes to the default database

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All migrations go to the default database; the airqualitydb is read-only.
        """
        if app_label in self.route_app_labels:
            return False
        return True
