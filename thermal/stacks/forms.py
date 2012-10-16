import hashlib
from horizon import exceptions
from horizon import forms

from django.core.cache import cache
#from django import forms

def generate_heat_form(heat_parameters):
    '''
    takes a dictionary of parameters from a heat template
    returns a form object created from the heat template
    '''
    # Collect the fields
    fields = {'StackName': forms.CharField(help_text='Unique name for the stack')}
    for param, val in heat_parameters.items():
        if 'AllowedValues' in val:
            choices = map(lambda x: (x,x), val['AllowedValues'])
            fields[param] = forms.ChoiceField(choices=choices)
        else:
            fields[param] = forms.CharField(initial=val.get('Default', None),
                                help_text=val.get('ConstraintDescription', ''))
        fields[param].initial=val.get('Default', None)
        fields[param].help_text=val.get('Description', '')
                                      # + val.get('ConstraintDescription', '')
    ####fields['launch_ha'] = forms.BooleanField(required=False) 
    # Create the form object
    base_form = type('HeatTemplateBaseForm', (forms.BaseForm,),
                                             { 'base_fields': fields })
    form = type('HeatTemplateForm',(forms.Form, base_form),{})
    # Set the fields order
    # This will have no effect if the params object is not
    # of type collections.OrderedDict
    # use object_pairs_hook=collections.OrderedDict on json.loads
    form.base_fields.keyOrder = heat_parameters.keys()
    form.base_fields.keyOrder.insert(0, 'StackName')
    ####form.base_fields.keyOrder.append('launch_ha')
    return form

class UploadTemplate(forms.SelfHandlingForm):
    template = forms.FileField()

    def handle(self, request, data):
        template = request.FILES['template'].read()
        cache.set('heat_template_' + request.user.username, template)
        return True
