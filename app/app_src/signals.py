from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

UserModel = get_user_model()

@receiver(m2m_changed, sender=UserModel.groups.through)
def update_user_permissions(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    users = [instance] if not reverse else UserModel.objects.filter(pk__in=pk_set)

    for user in users:
        is_admin = user.groups.filter(name="Admin").exists()
        is_assessor = user.groups.filter(name="Assessor").exists()

        user.is_superuser = is_admin
        user.is_staff = is_admin or is_assessor

        user.save(update_fields=["is_superuser", "is_staff"])