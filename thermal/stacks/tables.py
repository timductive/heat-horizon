import logging

from django.core import urlresolvers
from django.utils.http import urlencode
from django.template.defaultfilters import title
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon.utils.filters import replace_underscores

from thermal.models import Stack

LOG = logging.getLogger(__name__)


class LaunchStack(tables.LinkAction):
    name = "launch"
    verbose_name = _("Launch Stack")
    url = "horizon:thermal:stacks:upload"
    classes = ("ajax-modal", "btn-create")

class DeleteStack(tables.BatchAction):
    name = "delete"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of")
    data_type_singular = _("Stack")
    data_type_plural = _("Stacks")
    classes = ('btn-danger', 'btn-terminate')

    def allowed(self, request, stack=None):
        if stack:
            return True

    def action(self, request, stack_name):
        stack = Stack.objects.get(StackName=stack_name)
        stack.delete()

class StacksUpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, stack_name):
        try:
            stack = Stack.objects.get(StackName=stack_name)
        except:
            # probably didn't find the stack
            # should catch this better
            # for now maybe create an emptyone
            # to satisfy the ajax status updater?
            stack = None
        return stack

class ThermalStacksTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Create Complete", True),
        ("Create Failed", False),
    )
    TASK_DISPLAY_CHOICES = (
        ("image_snapshot", "Snapshotting"),
    )
    tenant = tables.Column("name", verbose_name=_("Stack Name"))
    created = tables.Column("created", verbose_name=_("Created"))
    updated = tables.Column("updated", verbose_name=_("Updated"))
    status = tables.Column("status",
                           filters=(title, replace_underscores),
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)

    class Meta:
        name = "stacks"
        verbose_name = _("Stacks")
        status_columns = ["status", ]
        table_actions = (LaunchStack, DeleteStack,)
        row_class = StacksUpdateRow
        row_actions = (DeleteStack, )
