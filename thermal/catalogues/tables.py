import httplib2

from django.core import urlresolvers
from django.core.cache import cache
from django.utils.http import urlencode
from django.http import Http404
from django.template.defaultfilters import title
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from horizon import tables
from horizon import messages
from horizon.utils.filters import replace_underscores

from thermal import CATALOGUES


class LaunchCatalogue(tables.Action):
    name = "launch"
    verbose_name = _("Launch")
    classes = ("btn-create", )#("ajax-modal", "btn-create")


    def _get_template(self, template_name):
        h = httplib2.Http(".cache",
                          disable_ssl_certificate_validation=True)
        url = '/'.join([CATALOGUES[cat_id]['base'], template_name])
        return h.request(url, "GET")

    def single(self, data_table, request, object_id):
        self.request = request
        cat_id = self.request.session.get('catalogue', None)
        # TODO: make cache dir configurable via django settings
        # TODO: make disabling ssl verification configurable too
        h = httplib2.Http(".cache",
                          disable_ssl_certificate_validation=True)
        url = CATALOGUES[cat_id]['base']
        if url[-1] == '/':
            url = '%s%s' % (url, object_id)
        else:
            url = '%s/%s' % (url, object_id)
        resp, template = h.request(url, "GET")
        if resp.status not in (200, 304):
            messages.error(self.request,
                           '%s returned status %s' % (url, resp.status))
            redirect_url = '%s?catalogue=%s' % (
                                   reverse("horizon:thermal:catalogues:index"),
                                   cat_id)
            return HttpResponseRedirect(redirect_url)
        # store the template so we can render it next
        request.session['heat_template'] = template
        request.session['heat_template_name'] = object_id
        return HttpResponseRedirect(reverse("horizon:thermal:stacks:launch"))


class ThermalCataloguesTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Template Name"),
                           link=("horizon:thermal:stacks:detail"),)
    size = tables.Column("size", verbose_name=_("Size"))

    class Meta:
        name = "catalogue"
        verbose_name = _("Catalogues")
        #status_columns = ["status", ]
        #table_actions = (LaunchCatalogue, DeleteStack,)
        #row_class = CataloguesUpdateRow
        row_actions = (LaunchCatalogue, )
