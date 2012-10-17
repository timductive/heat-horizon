import json
import collections

from horizon import forms
from django.db import models
from thermal.db import xml_models

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
        fields = {'StackName': forms.CharField(help_text='Unique name for the stack')}
        for param, val in self.json['Parameters'].items():
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
        form.base_fields.keyOrder = self.json['Parameters'].keys()
        form.base_fields.keyOrder.insert(0, 'StackName')
        ####form.base_fields.keyOrder.append('launch_ha')
        return form

class Stack(xml_models.Model):
    object_xpath = './/member'
    rest_all = 'list_stacks'
    rest_get = 'describe_stacks'
    client = None

    id = xml_models.CharField(xpath='/member/StackName')
    stackid = xml_models.CharField(xpath='/member/StackId')
    name = xml_models.CharField(xpath='/member/StackName')
    status = xml_models.CharField(xpath='/member/StackStatus')
    description = xml_models.CharField(xpath='/member/TemplateDescription')
    status_reason = xml_models.CharField(xpath='/member/StackStatusReason')
    created = xml_models.DateField(xpath='/member/CreationTime', date_format='%Y-%m-%dT%H:%M:%SZ')
    updated = xml_models.DateField(xpath='/member/LastUpdatedTime', date_format='%Y-%m-%dT%H:%M:%SZ')

    def __unicode__(self):
        return self.id

    def launch(self, template, parameters):
        '''
        take a json object and QueryDict of parameters
        and calls heat's api to launch a stack
        '''
        heat_template = json.loads(template)

        stack_name = parameters['StackName']
        del parameters['StackName'] # can't use pop because it's a QueryDict

        launch_parameters = {}
        for param in parameters:
            # have to be explicit like this because data is in a QueryDict
            if param in heat_template['Parameters'].keys():
                launch_parameters[param] = parameters[param]

        formatted_parameters = self.client.format_parameters(launch_parameters)
        formatted_parameters.update({'StackName': stack_name,
                           'TimeoutInMinutes': 5,
                           'TemplateBody': template, #json.dumps(template, sort_keys=False),
                          })
        # get the form params
        result = self.client.create_stack(**formatted_parameters)
        return result

    def delete(self):
        parameters = {'StackName': self.name}
        result = self.client.delete_stack(**parameters)
        return result
 
class StackCreate(xml_models.Model):
    object_xpath = './/CreateStackResult'

    StackId = xml_models.CharField(xpath='/StackId')
    StackName = xml_models.CharField(xpath='/StackName')
    Description = xml_models.CharField(xpath='/Description')
    Parameters = xml_models.CharField(xpath='/Parameters')
    

class EventResourceProperties(xml_models.Model):
    NovaSchedulerHints = xml_models.CharField(xpath='/member/ResourceProperties/NovaSchedulerHints')
    UserData = xml_models.CharField(xpath='/member/ResourceProperties/UserData')
    SourceDestCheck = xml_models.CharField(xpath='/member/ResourceProperties/SourceDestCheck')
    AvailabilityZone = xml_models.CharField(xpath='/member/ResourceProperties/AvailabilityZone')
    Monitoring = xml_models.CharField(xpath='/member/ResourceProperties/Monitoring')
    Volumes = xml_models.CharField(xpath='/member/ResourceProperties/Volumes')
    Tags = xml_models.CharField(xpath='/member/ResourceProperties/Tags')
    Tenancy = xml_models.CharField(xpath='/member/ResourceProperties/Tenancy')
    PlacementGroupName = xml_models.CharField(xpath='/member/ResourceProperties/PlacementGroupName')
    ImageId = xml_models.CharField(xpath='/member/ResourceProperties/ImageId')
    SubnetId = xml_models.CharField(xpath='/member/ResourceProperties/SubnetId')
    KeyName = xml_models.CharField(xpath='/member/ResourceProperties/KeyName')
    SecurityGroups = xml_models.CharField(xpath='/member/ResourceProperties/SecurityGroups')
    SecurityGroupIds = xml_models.CharField(xpath='/member/ResourceProperties/SecurityGroupIds')
    KernelId = xml_models.CharField(xpath='/member/ResourceProperties/KernelId')
    RamDiskId = xml_models.CharField(xpath='/member/ResourceProperties/RamDiskId')
    DisableApiTermination = xml_models.CharField(xpath='/member/ResourceProperties/DisableApiTermination')
    InstanceType = xml_models.CharField(xpath='/member/ResourceProperties/InstanceType')
    PrivateIpAddress = xml_models.CharField(xpath='/member/ResourceProperties/PrivateIpAddress')


class Event(xml_models.Model):
    object_xpath = './/member'
    rest_call = 'list_stack_events'

    EventId = xml_models.IntField(xpath='/member/EventId')
    StackId = xml_models.CharField(xpath='/member/StackId')
    ResourceStatus = xml_models.CharField(xpath='/member/ResourceStatus')
    ResourceType = xml_models.CharField(xpath='/member/ResourceType')
    Timestamp = xml_models.DateField(xpath='/member/Timestamp', date_format='%Y-%m-%dT%H:%M:%SZ')
    StackName = xml_models.CharField(xpath='/member/StackName')
    ResourceProperties = xml_models.CollectionField(EventResourceProperties, xpath='/member/ResourceProperties')
    PhysicalResourceId = xml_models.CharField(xpath='/member/PhysicalResourceId')
    ResourceStatusData = xml_models.CharField(xpath='/member/ResourceStatusData')
    LogicalResourceId = xml_models.CharField(xpath='/member/LogicalResourceId')

class ErrorResponse(xml_models.Model):
    object_xpath = './/Error'

    message = xml_models.CharField(xpath='/Message')
    code = xml_models.CharField(xpath='/Code')
    type = xml_models.CharField(xpath='/Type')
