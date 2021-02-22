import os
import dj_database_url

from physionet.settings.development.base import *

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(
        default='postgres://physionet:physionet@db:5432/physionet',
        conn_max_age=int(os.getenv('POSTGRES_CONN_MAX_AGE', 600))
    )
}
