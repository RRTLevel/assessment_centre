from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _


class DomainUnicodeUsernameValidator(UnicodeUsernameValidator):

    """Now supports \ character for domains associated with usernames"""

    regex = r'^[\w.@+-\\]+$'
    message = _(
        'Enter a valid username. This value may only contain letters, numbers, and \/@/./+/-/_ characters.'
    )