class MetabaseRouter:
    """
    A router to control all database operations on models in the
    metabase application.
    """

    route_app_labels = ["metabase"]

    def _db_from_model(self, model):
        if model._meta.app_label in self.route_app_labels:
            return "metabase"

    def db_for_read(self, model, **hints):
        return self._db_from_model(model)

    def db_for_write(self, model, **hints):
        return self._db_from_model(model)

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "metabase"
        return None