import hashlib
import httplib2

from horizon import messages
from horizon import forms

from django.core.cache import cache


class EditParameterForm(forms.SelfHandlingForm):
    name = forms.SlugField()
    Default = forms.CharField(required=False)
    NoEcho = forms.BooleanField(required=False)
    Description = forms.CharField(required=False)
    Type = forms.ChoiceField(choices=(('String','String'),))
    MinLength = forms.IntegerField(initial=1)
    MaxLength = forms.IntegerField(initial=64)
    AllowedPattern = forms.CharField(required=False)
    ConstraintDescription = forms.CharField(required=False)
    AllowedValues = forms.CharField(required=False)

    def handle(self, request, data):
        return False


class EditResourceForm(forms.SelfHandlingForm):
    name = forms.SlugField()
    description = forms.CharField()

    def handle(self, request, data):
        return False


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
        # No template validation is done here, We'll let heat do that for us
        return True
