import logging

from django.core import urlresolvers
from django.utils.http import urlencode
from django.template.defaultfilters import title
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon.utils.filters import replace_underscores

from thermal.models import Stack

LOG = logging.getLogger(__name__)


class DeleteStack(tables.LinkAction):
    name = "delete"
    verbose_name = _("Delete Stack")
    url = "horizon:project:access_and_security:floating_ips:associate"
    classes = ("ajax-modal", "btn-associate")

    #def allowed(self, request, instance):
    #    return not _is_deleting(instance)

    def get_link_url(self, datum):
        base_url = urlresolvers.reverse(self.url)
        next = urlresolvers.reverse("horizon:project:instances:index")
        params = {"name": self.table.get_object_id(datum),}
        #          IPAssociationWorkflow.redirect_param_name: next}
        params = urlencode(params)
        return "?".join([base_url, params])


class StacksUpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, stack_name):
        stack = Stack.objects.get(StackName=stack_name)
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
#        table_actions = (DeleteStack,)
        row_class = StacksUpdateRow
#        row_actions = (DeleteStack, )
