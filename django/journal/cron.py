from django_cron import CronJobBase, Schedule

from journal.models import Editor
from journal.emailutils import send_commission_reminder


# To make this actually run, add `python manage.py runcrons` to crontab.
class DailyCommissionUpdate(CronJobBase):
    RUN_EVERY_MINS = 1400  # 24 hours
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'journal.daily_commission_update'

    def do(self):
        output = []
        for editor in Editor.objects.filter(wants_emails=True):
            status = send_commission_reminder(editor)
            output.append(
                "{name}: {status}".format(
                    name=editor.author.name,
                    status=status
                )
            )

        return '\n'.join(output)
