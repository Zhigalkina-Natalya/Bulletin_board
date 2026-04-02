from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Создание групп и прав"

    def handle(self, *args, **kwargs):
        content_manager, _ = Group.objects.get_or_create(name="Content Manager")

        permissions = Permission.objects.filter(
            codename__in=[
                "add_category",
                "change_category",
                "delete_category",
                "view_category",
                "change_ad",
                "delete_ad",
                "view_ad",
            ]
        )

        content_manager.permissions.set(permissions)

        self.stdout.write(self.style.SUCCESS("Группы созданы"))
