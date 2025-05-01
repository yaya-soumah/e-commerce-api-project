from django.core.management.base import BaseCommand
from users.models import UserProfile, User

class Command(BaseCommand):
    help = 'Creates UserProfile for users without one'

    def handle(self, *args, **kwargs):
        users_without_profile = User.objects.filter(profile__isnull=True)
        count = 0
        for user in users_without_profile:
            UserProfile.objects.create(user=user)
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} UserProfile records'))