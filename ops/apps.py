from django.apps import AppConfig


class OpsConfig(AppConfig):
    name = 'ops'

    def ready(self):
        import ops.signals
