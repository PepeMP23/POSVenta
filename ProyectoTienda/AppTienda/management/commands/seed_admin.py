from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

class Command(BaseCommand):
    help = "Crea el admin inicial (admin@company.com / ADMIN) si no existe"

    def handle(self, *args, **opts):
        User = get_user_model()
        email = f"admin@{settings.CORPORATE_EMAIL_DOMAINS[0]}"
        if not User.objects.filter(email=email).exists():
            u = User.objects.create_superuser(email=email, password="ADMIN", role="admin")
            self.stdout.write(self.style.SUCCESS(f"Admin creado: {email} / ADMIN"))
        else:
            self.stdout.write(self.style.WARNING("El admin inicial ya existe."))
