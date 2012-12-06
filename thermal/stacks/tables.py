import logging

from django.core import urlresolvers
from django.utils.http import urlencode
from django.http import Http404
from django.template.defaultfilters import title
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from horizon import tables
from horizon.utils.filters import replace_underscores
from horizon import messages

from heatclient import exc

from thermal.api import heatclient

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

    def action(self, request, stack_id):
        heatclient(request).stacks.delete(stack_id)


class StacksUpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, stack_id):
        try:
            return heatclient(request).stacks.get(stack_id)
        except exc.HTTPNotFound:
            # returning 404 to the ajax call removes the
            # row from the table on the ui
            raise Http404
        except Exception, e: 
            messages.error(request, e)


class ThermalStacksTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Create Complete", True),
        ("Create Failed", False),
    )
    name = tables.Column("stack_name", verbose_name=_("Stack Name"),
                           link="horizon:thermal:stacks:detail",)       
    created = tables.Column("creation_time", verbose_name=_("Created"))
    updated = tables.Column("updated_time", verbose_name=_("Updated"))
    status = tables.Column("stack_status",
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


def thermal_events_table_instance_link(datum):
    if datum.physical_resource_id is None or \
       datum.physical_resource_id == 'None':
        # All the Physical Resource ID's are sometimes 'None'
        # return None when this is the case to indicate not
        # to link the instance name
        return None
    # Otherwise link the project instance details
    url = reverse('horizon:project:instances:detail',
                  args=(datum.physical_resource_id,))
    return url

class ThermalEventsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Create Complete", True),
        ("Create Failed", False),
    )
    event_time = tables.Column("event_time", verbose_name=_("Event Time"))
    logical_resource = tables.Column("logical_resource_id",
                                     verbose_name=_("Logical Resource"),
                                     link=thermal_events_table_instance_link,)
    status = tables.Column("resource_status",
                           filters=(title, replace_underscores),
                           verbose_name=_("Status"),)

    status_reason = tables.Column("resource_status_reason",
                                 verbose_name=_("Status Reason"),)

    class Meta:
        name = " "
        verbose_name = _(" ")
