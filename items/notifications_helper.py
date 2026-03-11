from django.core.mail import send_mail
from django.conf import settings


def send_notification(user, notif_type, title, message, item=None):
    from claims.models import Notification
    Notification.objects.create(
        user=user,
        notif_type=notif_type,
        title=title,
        message=message,
        item=item,
    )
    if user.email:
        try:
            send_mail(
                subject=f'Campus Found - {title}',
                message=f'Hi {user.username},\n\n{message}\n\nVisit Campus Found to view details.\n\nCampus Found Team',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass


def notify_claim_received(item, claimant):
    send_notification(
        user=item.owner,
        notif_type='claim_received',
        title='Someone claimed your item',
        message=f'{claimant.username} submitted a claim for your item "{item.title}".',
        item=item,
    )


def notify_claim_approved(claim):
    send_notification(
        user=claim.claimant,
        notif_type='claim_approved',
        title='Your claim was approved!',
        message=f'Your claim for "{claim.item.title}" has been approved. Contact the owner to arrange pickup.',
        item=claim.item,
    )


def notify_claim_rejected(claim):
    send_notification(
        user=claim.claimant,
        notif_type='claim_rejected',
        title='Your claim was rejected',
        message=f'Your claim for "{claim.item.title}" has been rejected.',
        item=claim.item,
    )


def notify_item_deleted(user, item_title):
    send_notification(
        user=user,
        notif_type='item_deleted',
        title='Your item was removed',
        message=f'Your item "{item_title}" has been removed by an admin.',
        item=None,
    )


def notify_item_match(lost_item, found_item):
    send_notification(
        user=lost_item.owner,
        notif_type='item_match',
        title='Possible match found!',
        message=f'A found item "{found_item.title}" at {found_item.location} may match your lost item "{lost_item.title}".',
        item=found_item,
    )