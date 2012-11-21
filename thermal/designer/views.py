import json

from xml.etree import ElementTree as et

from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.core.cache import cache

from horizon import tabs
from horizon import forms

from thermal.models import HeatTemplate
from thermal.api import heatclient

from .tabs import DesignerTabs
from .forms import EditParameterForm
from .forms import EditResourceForm


class IndexView(tabs.TabView):
    tab_group_class = DesignerTabs
    template_name = 'thermal/designer/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context

    def get_data(self, request, **kwargs):
        return ''
    #    if not hasattr(self, "_stack"):
    #        print kwargs
    #        stack_id = kwargs['stack_id']
    #        try:
    #            stack = heatclient(request).stacks.get(stack_id)
    #            self._stack = stack
    #        except Exception, e:
    #            messages.error(request, e)
    #            redirect = reverse('horizon:thermal:stacks:index')
    #            return HttpResponseRedirect(redirect)
    #    return self._stack

    def get_tabs(self, request, **kwargs):
        stack = self.get_data(request, **kwargs)
        return self.tab_group_class(request, stack=stack, **kwargs)

    def post(self, request):
        resources = {}
        template_html = '<template>%s</template>' % \
                                request.POST.get('template', '')
        print template_html
        print request.POST
        root = et.fromstring(template_html) 
        for child in root:
            if 'id' in child.attrib:
                resources[child.attrib['id']] = { 
                    'Type': "AWS::EC2::Instance",
                    #'Metadata':,
                    #'Properties':,
                }

        template = {
            "AWSTemplateFormatVersion" : "2010-09-09",
            "Description" : request.POST.get('description', ''),
            #"Parameters": {},
            "Resources": resources,
            #"Output": {},
        }

        print template
        cache.set('designer_template', template)
        return HttpResponse(json.dumps(template))


class ParameterEditView(forms.ModalFormView):
    form_class = EditParameterForm
    template_name = 'thermal/designer/parameter.html'

    def form_valid(self, form):
        try:
            handled = form.handle(self.request, form.cleaned_data)
        except:
            handled = None
            exceptions.handle(self.request)

        if handled:
            form.cleaned_data['type'] = 'parameter'
            data = json.dumps(form.cleaned_data)
            wrapped = '<div id="modal_response">%s</div>' % data
            response = HttpResponse(wrapped)
            return response
        else:
            # If handled didn't return, we can assume something went
            # wrong, and we should send back the form as-is.
            return self.form_invalid(form)


class ResourceEditView(forms.ModalFormView):
    form_class = EditResourceForm
    template_name = 'thermal/designer/resource.html'

    def form_valid(self, form):
        try:
            handled = form.handle(self.request, form.cleaned_data)
        except:
            handled = None
            exceptions.handle(self.request)

        if handled:
            form.cleaned_data['type'] = 'resource'
            data = json.dumps(form.cleaned_data)
            wrapped = '<div id="modal_response">%s</div>' % data
            response = HttpResponse(wrapped)
            return response
        else:
            # If handled didn't return, we can assume something went
            # wrong, and we should send back the form as-is.
            return self.form_invalid(form)
