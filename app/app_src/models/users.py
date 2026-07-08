from django.contrib.auth.models import User

from ..validators import DomainUnicodeUsernameValidator


class DomainUser(User):
    """Proxy user that accepts DOMAIN\\username style usernames."""

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field("username").validators = [
            DomainUnicodeUsernameValidator()
        ]
