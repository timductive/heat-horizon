import json
import collections

from horizon import tables
from horizon import forms

from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.core.cache import cache

from thermal.stacks.tables import ThermalStacksTable
from thermal.models import Stack
from thermal.api import heatclient

from .forms import generate_heat_form
from .forms import UploadTemplate

class IndexView(tables.DataTableView):
    table_class = ThermalStacksTable
    template_name = 'thermal/stacks/index.html'

    def get_data(self):
        return Stack.objects.all(self.request)

class LaunchHeatView(forms.ModalFormView):
    template_name = 'thermal/stacks/launch.html'
    success_url = reverse_lazy('horizon:thermal:stacks:index')

    def get(self, request, *args, **kw):
        template = cache.get('heat_template_' + request.user.username)
        heat_template = json.loads(template,
                                   object_pairs_hook=collections.OrderedDict)
        form = generate_heat_form(heat_template['Parameters'])
        self.form_class = form
        context = {'form': form()}
        return self.render_to_response(context)

    def post(self, request, *args, **kw):
        template = cache.get('heat_template_' + request.user.username)
        client = heatclient(request)
        result = Stack(client).launch(template, request.POST.copy())
        return HttpResponseRedirect(self.success_url)

class UploadView(forms.ModalFormView):
    form_class = UploadTemplate
    template_name = 'thermal/stacks/upload.html'
    success_url = reverse_lazy('horizon:thermal:stacks:launch')
