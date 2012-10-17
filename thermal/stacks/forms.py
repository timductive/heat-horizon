import hashlib
from horizon import exceptions
from horizon import forms

from django.core.cache import cache
#from django import forms

class UploadTemplate(forms.SelfHandlingForm):
    template = forms.FileField()

    def handle(self, request, data):
        template = request.FILES['template'].read()
        cache.set('heat_template_' + request.user.username, template)
        return True
