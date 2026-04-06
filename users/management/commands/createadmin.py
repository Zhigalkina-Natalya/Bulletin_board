from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = "Создание администратора через input"

    def handle(self, *args, **options):
        email = input("Введите email администратора: ").strip()

        password = input("Введите пароль администратора: ").strip()

        try:
            user, created = User.objects.get_or_create(email=email, defaults={"is_staff": True, "is_superuser": True})
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Администратор успешно создан с email {email}"))
            else:
                self.stdout.write(self.style.WARNING("Администратор уже существует"))
        except IntegrityError:
            self.stdout.write(self.style.WARNING("Администратор уже существует (ошибка базы данных)"))
