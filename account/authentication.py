from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameModelBackend(object):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # ইউজারনেম অথবা ইমেইল যেকোনো একটা মিললেই ইউজারকে খুঁজে বের করবে
            user = User.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None