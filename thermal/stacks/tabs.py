from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("thermal/stacks/_detail_overview.html")

    def get_context_data(self, request):
        return {"stack": self.tab_group.kwargs['stack']}


class EventsTab(tabs.Tab):
    name = _("Events")
    slug = "events"
    template_name = "thermal/stacks/_detail_events.html"
    preload = False

    def get_context_data(self, request):
        instance = self.tab_group.kwargs['instance']
        try:
            data = api.server_console_output(request,
                                            instance.id,
                                            tail_length=35)
        except:
            data = _('Unable to get log for instance "%s".') % instance.id
            exceptions.handle(request, ignore=True)
        return {"instance": instance,
                "console_log": data}


class StackDetailTabs(tabs.TabGroup):
    slug = "stack_details"
    tabs = (OverviewTab, EventsTab)
    sticky = True
