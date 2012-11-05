import json
import collections

from horizon import forms
from django.db import models


class HeatTemplate(object):
    template = None
    json = None
    form = None

    def __init__(self, template, passback=None):
        # get uploaded form from the cache
        self.template = template
        self.json = json.loads(template,
                               object_pairs_hook=collections.OrderedDict)
        self.form = self.generate_heat_form()
        if passback:
            passback = self.form

    def generate_heat_form(self):
        '''
        takes a HeatTemplate object
        returns a form object created from the heat template
        '''
        # Collect the fields
        fields = {'stack_name': forms.CharField(
                                   help_text='Unique name for the stack')}
        for param, val in self.json['Parameters'].items():
            if 'AllowedValues' in val:
                choices = map(lambda x: (x, x), val['AllowedValues'])
                fields[param] = forms.ChoiceField(choices=choices)
            else:
                fields[param] = forms.CharField(
                                    initial=val.get('Default', None),
                                    help_text=val.get('ConstraintDescription',
                                                      ''))
            fields[param].initial = val.get('Default', None)
            fields[param].help_text = val.get('Description', '')
                                       # + val.get('ConstraintDescription', '')
        ####fields['launch_ha'] = forms.BooleanField(required=False)
        # Create the form object
        base_form = type('HeatTemplateBaseForm', (forms.BaseForm,),
                                                 {'base_fields': fields})
        form = type('HeatTemplateForm', (forms.Form, base_form), {})
        # Set the fields order
        # This will have no effect if the params object is not
        # of type collections.OrderedDict
        # use object_pairs_hook=collections.OrderedDict on json.loads
        form.base_fields.keyOrder = self.json['Parameters'].keys()
        form.base_fields.keyOrder.insert(0, 'stack_name')
        ####form.base_fields.keyOrder.append('launch_ha')
        return form
