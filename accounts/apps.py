from django.apps import AppConfig


class Accounts(AppConfig):
    name = 'accounts'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import accounts.signals