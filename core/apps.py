from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    
    def ready(self):
        """
        After migrations complete, ensure a default superuser exists.
        Creates username 'core' with password 'core' if not present.
        """
        from django.db.models.signals import post_migrate
        from django.contrib.auth import get_user_model

        def create_default_superuser(sender, **kwargs):
            User = get_user_model()
            username = "core"
            password = "core"
            try:
                if not User.objects.filter(username=username).exists():
                    User.objects.create_superuser(
                        username=username,
                        email="core@example.com",
                        password=password,
                    )
            except Exception:
                # Swallow exceptions to avoid breaking migrations; can log if needed.
                pass

        # Connect the signal only once per app registry load.
        post_migrate.connect(create_default_superuser, sender=self)
