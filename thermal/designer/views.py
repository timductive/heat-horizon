import json

from xml.etree import ElementTree as et

from django.views.generic import TemplateView
from django.http import HttpResponse
from django.core.cache import cache

from horizon import tabs

from thermal.models import HeatTemplate
from thermal.api import heatclient

from .tabs import DesignerTabs


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
