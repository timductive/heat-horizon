import hashlib
import httplib2

from horizon import messages
from horizon import forms

from django.core.cache import cache


class UploadTemplate(forms.SelfHandlingForm):
    upload_template = forms.FileField(required=False)
    http_url = forms.CharField(required=False)

    def handle(self, request, data):
        if 'upload_template' in request.FILES:
            # local file upload
            template = request.FILES['upload_template'].read()
            template_name = request.FILES['upload_template'].name
        elif 'http_url' in request.POST and request.POST['http_url']:
            # download from a given url
            url = request.POST['http_url']
            template_name = url.split('/')[-1]
            # TODO: make cache dir configurable via django settings
            # TODO: make disabling ssl verification configurable too
            h = httplib2.Http(".cache",
                              disable_ssl_certificate_validation=True)
            resp, template = h.request(url, "GET")
            if resp.status not in (200, 304):
                messages.error(request, 'URL returned status %s' % resp.status)
                return False
        else:
            # neither file or url were given
            messages.error(request, "Please choose a file or provide a url")
            return False

        # store the template so we can render it next
        cache.set('heat_template_' + request.user.username, template)
        cache.set('heat_template_name_' + request.user.username, template_name)
        # No template validation is done here, We'll let heat do that for us
        return True
