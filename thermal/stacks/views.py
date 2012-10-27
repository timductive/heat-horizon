import json

from horizon import tables
from horizon import forms
from horizon import messages
from horizon import exceptions
from horizon import tabs

from django.core.urlresolvers import reverse_lazy
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.core.cache import cache
from django.views import generic

from thermal.stacks.tables import ThermalStacksTable
from thermal.models import Stack
from thermal.models import HeatTemplate
from thermal.models import ErrorResponse
from thermal.api import heatclient

from .forms import UploadTemplate
from .tabs import StackDetailTabs

class IndexView(tables.DataTableView):
    table_class = ThermalStacksTable
    template_name = 'thermal/stacks/index.html'

    def get_data(self):
        return Stack.objects.all(self.request)

class LaunchHeatView(generic.FormView):
    template_name = 'thermal/stacks/launch.html'
    success_url = reverse_lazy('horizon:thermal:stacks:index')

    def get(self, request, *args, **kw):
        template = cache.get('heat_template_' + request.user.username)
        t = HeatTemplate(template, self.form_class)
        context = {'form': t.form()}
        return self.render_to_response(context)

    def post(self, request, *args, **kw):
        template = cache.get('heat_template_' + request.user.username)
        t = HeatTemplate(template, self.form_class)
        form = t.form(request.POST)
        client = heatclient(request)
        if form.is_valid():
            try:
                s = Stack(client)
                result = s.launch(template, form.cleaned_data)
            except Exception, e:
                # TODO: fix this so the xml does't display
                #err_xml = e._error_string[e._error_string.find('<'):]
                #err = ErrorResponse(client, xml=err_xml)
                #err_msg = e.message % {'reason': '%s %s' % (err.code, err.message)}
                #import pdb
                #pdb.set_trace()
                messages.error(request, e)
                return self.render_to_response({'form': form})
        return HttpResponseRedirect(self.success_url)

class UploadView(forms.ModalFormView):
    form_class = UploadTemplate
    template_name = 'thermal/stacks/upload.html'
    success_url = reverse_lazy('horizon:thermal:stacks:launch')

class DetailView(tabs.TabView):
    tab_group_class = StackDetailTabs
    template_name = 'thermal/stacks/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["stack"] = self.get_data(self.request)
        return context

    def get_data(self, request, **kwargs):
        if not hasattr(self, "_stack"):
            try:
                stack_name = kwargs['stack_name']
                stack = Stack.objects.get(request, StackName=stack_name)

                #stack.events = api.server_security_groups(
                #                           self.request, instance_id)
            except:
                redirect = reverse('horizon:thermal:stacks:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'stack "%s".') % stack_name,
                                    redirect=redirect)
            self._stack = stack
        return self._stack

    def get_tabs(self, request, **kwargs):
        stack = self.get_data(request, **kwargs)
        return self.tab_group_class(request, stack=stack, **kwargs)
