from celery import Celery

app = Celery(
    "worker", backend="redis://192.168.0.215:9654", broker="amqp://192.168.0.215:1070//"
)

app.conf.update(
    broker_pool_limit=None,
    task_acks_late=True,
    broker_heartbeat=None,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
    result_expires=86400,  # one day,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Seoul",
    enable_utc=False
    # worker_cancel_long_running_tasks_on_connection_loss=True,
    # task_reject_on_worker_lost=True,
    # task_queue_max_priority=10
)