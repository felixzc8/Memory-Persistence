from celery import Celery
from celery.signals import worker_process_init
from TiMemory.config.base import MemoryConfig
import logging
import logfire

config = MemoryConfig()

@worker_process_init.connect()
def init_worker_process(*args, **kwargs):
    if not hasattr(logfire, '_configured'):
        logfire.configure(
            service_name="worker", 
            token=config.logfire_token,
        )
        logfire.instrument_celery()
        
        logging.basicConfig(handlers=[logfire.LogfireLoggingHandler()], level=logging.INFO, force=True)
        logfire._configured = True

celery_app = Celery(
    broker=f"redis://{config.redis_host}:{config.redis_port}/{config.redis_db}",
    backend=f"redis://{config.redis_host}:{config.redis_port}/{config.redis_db}",
    include=["TiMemory.tasks.memory_tasks"]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

print(f"Celery app configured with Redis broker: {config.redis_host}:{config.redis_port}")