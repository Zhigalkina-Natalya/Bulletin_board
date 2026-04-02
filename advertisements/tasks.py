from celery import shared_task


@shared_task
def notify_new_ad(ad_title):
    """Имитация отправки уведомления о новом объявлении."""
    print(f"Новое объявление создано: {ad_title}")
