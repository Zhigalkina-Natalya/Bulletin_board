from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    """Команда создания администратора."""

    def handle(self, *args, **options):
        if User.objects.filter(email="admin@example.com").exists():
            self.stdout.write(self.style.WARNING("Администратор уже существует"))
            return

        user = User.objects.create(email="admin@example.com")
        user.set_password("12345")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Администратор успешно создан с email {user.email}"))
