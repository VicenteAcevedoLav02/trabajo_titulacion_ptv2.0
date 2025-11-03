import os
from celery import Celery

# Establecer el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ptv_controller.settings')

# Crear la instancia de Celery
app = Celery('ptv_controller')

# Configuración desde settings.py con el prefijo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescubrir tareas en las apps instaladas (buscará tasks.py en cada app)
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')