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

from thermal.models import HeatTemplate
from thermal import api

from .tables import ThermalStacksTable
from .forms import UploadTemplate
from .tabs import StackDetailTabs


class IndexView(tables.DataTableView):
    table_class = ThermalStacksTable
    template_name = 'thermal/stacks/index.html'

    def _inject_name(self, stack):
        # Horizon expects the object to have a name property
        # in order for the delete functionality to work properly
        # this function is mapped onto a stack object
        # setting the name property equal to the stack_name
        stack.name = stack.stack_name
        return stack

    def get_data(self):
        stacks = api.heat.stacks_list(self.request)
        stacks = map(self._inject_name, stacks)
        return stacks


class LaunchHeatView(generic.FormView):
    template_name = 'thermal/stacks/launch.html'
    success_url = reverse_lazy('horizon:thermal:stacks:index')

    def get(self, request, *args, **kw):
        template = cache.get('heat_template_' + request.user.username)
        template_name = cache.get('heat_template_name_' + request.user.username)
        if template is None:
            if 'HTTP_REFERER' in request.META:
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            else:
                return HttpResponseRedirect(reverse('horizon:thermal:stacks:upload'))
        t = HeatTemplate(template)
        context = {'form': t.form(),
                   'template_name': template_name}
        return self.render_to_response(context)

    def post(self, request, *args, **kw):
        template = cache.get('heat_template_' + request.user.username)
        template_name = cache.get('heat_template_name_' + request.user.username)
        if template is None:
            if 'HTTP_REFERER' in request.META:
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            else:
                return HttpResponseRedirect(reverse('horizon:thermal:stacks:upload'))
        t = HeatTemplate(template)
        form = t.form(request.POST)
        if form.is_valid():
            try:
                stack_name = form.cleaned_data.pop('stack_name')
                params = {'stack_name': stack_name,
                          'template': t.json,
                          'parameters': form.cleaned_data,}
                result = api.heat.stacks_create(request, params)
            except Exception, e:
                messages.error(request, e)
                return self.render_to_response({'form': form,
                                                'template_name': template_name})
        else:
            return self.render_to_response({'form': form,
                                                'template_name': template_name})
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
            stack_id = kwargs['stack_id']
            try:
                stack = api.heat.stacks_get(request, stack_id)
                self._stack = stack
            except Exception, e:
                messages.error(request, e)
                redirect = reverse('horizon:thermal:stacks:index')
                return HttpResponseRedirect(redirect)
        return self._stack

    def get_tabs(self, request, **kwargs):
        stack = self.get_data(request, **kwargs)
        return self.tab_group_class(request, stack=stack, **kwargs)
