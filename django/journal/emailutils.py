import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.template import loader

from journal.models import Article, Commission, Editor



ADMIN_EMAIL = 'ilostwaldo@gmail.com'
def send_email(to_email, subject, template, context):
    title = subject
    context['title'] = subject
    html_message = loader.render_to_string(template, context)
    message = subject  # surely this should never show?

    # Add ilostwaldo@gmail.com if that's not the to_email
    recipient_list = [to_email]
    if to_email != ADMIN_EMAIL:
        recipient_list.append(ADMIN_EMAIL)

    sent = send_mail(
        subject=title,
        message=message,
        from_email='New Socialist <website@newsocialist.org.uk>',
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False
    )
    if sent:
        return "Sent"
    else:
        return "Failed to send"


def send_commission_reminder(editor):
    today = datetime.date.today()
    counts = {
        'total': Commission.objects.count(),
        'active': Commission.objects.filter(needs_action=True).count(),
        'inactive': Commission.objects.filter(needs_action=False).count(),
    }

    commissions = editor.get_overdue_commissions()
    active_commissions = commissions.filter(needs_action=True)
    inactive_commissions = commissions.filter(needs_action=False)

    # Only send if this editor has overdue commissions or, if the editor is
    # an online editor, also articles.
    should_send = False
    if active_commissions.count() or inactive_commissions.count():
        should_send = True

    if editor.is_online_editor:
        articles = Article.objects.filter(date__lte=today).exclude(published=True)
        if articles.count():
            should_send = True

        # For online editors, also show the commissions that others should be
        # taking care of.
        other_commissions = Commission.objects.exclude(
            editor=editor,
        ).filter(
            remind_after__lte=today,
        )
    else:
        articles = Article.objects.none()
        other_commissions = Commission.objects.none()

    if should_send:
        return send_email(
            to_email=editor.user.email,
            subject='NS Commission Reminder',
            template='email/commission_reminder.html',
            context={
                'host': settings.SITE_URL,
                'name': editor.user.first_name,
                'active_commissions': active_commissions,
                'inactive_commissions': inactive_commissions,
                'other_commissions': other_commissions,
                'articles': articles,
                'counts': counts,
            },
        )
    else:
        return "Not sending"


def send_test():
    editor = Editor.objects.get(pk=5)
    send_commission_reminder(editor)
