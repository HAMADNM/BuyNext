import requests
import os
from django.core.files.base import ContentFile
from django.dispatch import receiver
from django.db.models.signals import post_delete
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_updated
from .models import User


print("SIGNALS FILE LOADED")


@receiver(user_signed_up)
def save_google_profile_picture(request, user, sociallogin=None, **kwargs):

    if sociallogin:
        extra_data = sociallogin.account.extra_data

        user.is_email_verified = True

        picture_url = extra_data.get("picture")

        if picture_url and not user.profile_image:
            try:
                response = requests.get(picture_url, timeout=5)

                if response.status_code == 200:
                    user.profile_image.save(
                        f"{user.id}_google.jpg",
                        ContentFile(response.content),
                        save=False
                    )

            except Exception as e:
                print("Image download failed:", e)

        user.save()


@receiver(social_account_updated)
def update_google_user(request, sociallogin, **kwargs):
    user = sociallogin.user

    if not user.is_email_verified:
        user.is_email_verified = True
        user.save()


@receiver(post_delete, sender=User)
def delete_user_image(sender, instance, **kwargs):
    if instance.profile_image:
        try:
            if os.path.isfile(instance.profile_image.path):
                os.remove(instance.profile_image.path)
        except Exception as e:
            print("Error deleting image:", e)