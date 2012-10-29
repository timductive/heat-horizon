import logging

from django.core import urlresolvers
from django.utils.http import urlencode
from django.http import Http404
from django.template.defaultfilters import title
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

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
        stack = Stack.objects.get(request, StackName=stack_name)
        stack.delete()


class StacksUpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, stack_name):
        try:
            stack = Stack.objects.get(request, StackName=stack_name)
        except:
            # TODO: read the actual error and make sure we're
            # getting a stack-does-not-exist error
            raise Http404
        return stack


class ThermalStacksTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Create Complete", True),
        ("Create Failed", False),
    )
    TASK_DISPLAY_CHOICES = (
        ("image_snapshot", "Snapshotting"),
    )
    tenant = tables.Column("name", verbose_name=_("Stack Name"),
                           link=("horizon:thermal:stacks:detail"),)
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


def thermal_events_table_instance_name(datum):
    return '%s.%s' % (datum.stackname, datum.logicalresourceid) 

def thermal_events_table_instance_link(datum):
    if datum.physicalresourceid is None or \
       datum.physicalresourceid == 'None':
        # All the Physical Resource ID's are sometimes 'None'
        # return None when this is the case to indicate not
        # to link the instance name
        return None
    # Otherwise link the project instance details
    url = reverse('horizon:project:instances:detail',
                  args=(datum.physicalresourceid,))
    return url

class ThermalEventsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Create Complete", True),
        ("Create Failed", False),
    )
    timestamp = tables.Column("timestamp", verbose_name=_("Timestamp"))
    stackname = tables.Column("stackname", verbose_name=_("stackname"))
    logical_resource = tables.Column(thermal_events_table_instance_name,
                                     verbose_name=_("Logical Resource"),
                                     link=thermal_events_table_instance_link,)
    status = tables.Column("resourcestatus",
                           filters=(title, replace_underscores),
                           verbose_name=_("Status"),)

    statusreason = tables.Column("resourcestatusreason",
                                 verbose_name=_("Status Reason"),)

    class Meta:
        name = " "
        verbose_name = _(" ")
