from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Claim, Notification
from django.conf import settings


def send_and_notify(user, message, subject, recipient_email):
    Notification.objects.create(user=user, message=message)

    send_mail(
        subject = subject,
        message = message,
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently = False,
    )


@receiver(post_save, sender=Claim)

def claim_notification_handler(sender, instance, created, **kwargs):
    claim = instance
    claimant = claim.claimant
    owner = claim.item.owner


    if created:
        send_and_notify(
            user  = owner,
            message=(
                f"someone has submitted a claim on your item '{claim.item.title}'."
                f"Log in to review the claim and take necessary action."
            ),
            subject = "New Claim Submitted",
            recipient_email = owner.email,
        )

    
    elif claim.status == 'Approved':

        send_and_notify(
            user = claimant,
            message = (
                f"Congratulations! Your claim for the item '{claim.item.title}' has been approved."
                f"Please contact the owner to arrange for the return of your item."
            ),
            subject = "Claim Approved",
            recipient_email = claimant.email,
        )

        owner.reputation_score = (owner.reputation_score or 0) + 5
        owner.save(update_fields=['reputation_score'])


    elif claim.status == 'Rejected':
        send_and_notify(
            user = claimant,
            message = (
                f"Unfortunately, your claim for the item '{claim.item.title}' has been rejected."
                f"Please review the proof you provided and consider submitting a new claim if you have additional information."
            ),
            subject = "Claim Rejected",
            recipient_email = claimant.email,
        )

        owner.reputation_score = (owner.reputation_score or 0) - 2
        owner.save(update_fields=['reputation_score'])