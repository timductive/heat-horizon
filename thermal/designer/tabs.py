import json

from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache

from horizon import exceptions
from horizon import tabs


class DesignTab(tabs.Tab):
    name = _("Design")
    slug = "design"
    template_name = ("thermal/designer/_design.html")

    def get_context_data(self, request):
        return {}


class RenderTab(tabs.Tab):
    name = _("Render")
    slug = "render"
    template_name = "thermal/designer/_render.html"
    preload = False

    def get_context_data(self, request):
        template = cache.get('designer_template', '')
        return {"template": template, }


class DesignerTabs(tabs.TabGroup):
    slug = "designer_tabs"
    tabs = (DesignTab, RenderTab)
    #sticky = True
