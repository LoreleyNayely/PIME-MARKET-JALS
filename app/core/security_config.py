from decouple import config


class SecurityConfig:
    JWT_SECRET_KEY = config('JWT_SECRET_KEY')
    JWT_ALGORITHM = config('JWT_ALGORITHM', default='HS256')
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config(
        'JWT_ACCESS_TOKEN_EXPIRE_MINUTES', default=30, cast=int)
    AES_SECRET_KEY = config('AES_SECRET_KEY')
