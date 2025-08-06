from decouple import config


class Properties():
    CLIENTS_URL = config('CLIENTS_URL')
    LOGS_ENABLE = config('LOGS_ENABLE', cast=bool)
