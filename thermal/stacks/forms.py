import hashlib
import httplib2

from horizon import messages
from horizon import forms

from django.core.cache import cache
#from django import forms

class UploadTemplate(forms.SelfHandlingForm):
    upload_template = forms.FileField(required=False)
    http_url = forms.CharField(required=False)

    def handle(self, request, data):
        if 'upload_template' in request.FILES:
            # local file upload
            template = request.FILES['upload_template'].read()
        elif 'http_url' in request.POST and request.POST['http_url']:
            # download from a given url
            url = request.POST['http_url']
            # TODO: make cache dir configurable via django settings
            h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
            resp, template = h.request(url, "GET")
            if resp.status not in (200, 304):
                messages.error(request, 'URL returned status code %s' % resp.status)
                return False
        else:
            # neither file or url were given
            messages.error(request, "Please choose a file or provide a url")
            return False

        # store the template so we can render it next
        cache.set('heat_template_' + request.user.username, template)
        # No template validation is done here, We'll let heat do that for us
        return True
