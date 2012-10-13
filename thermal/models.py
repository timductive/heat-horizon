import json

from django.db import models
from thermal.db import xml_models

class Stack(xml_models.Model):
    object_xpath = './/member'
    rest_all = 'list_stacks'
    rest_get = 'describe_stacks'

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

    @staticmethod
    def launch(template, parameters):
        '''
        take a json object and QueryDict of parameters
        and calls heat's api to launch a stack
        '''
        c = heatclient(request)
        stack_name = parameters['StackName']
        del parameters['StackName'] # can't use pop because it's a QueryDict

        launch_parameters = {}
        for param in parameters:
            # have to be explicit like this because data is in a QueryDict
            if param in template['Parameters'].keys():
                launch_parameters[param] = parameters[param]

        formatted_parameters = c.format_parameters(launch_parameters)
        formatted_parameters.update({'StackName': stack_name,
                           'TimeoutInMinutes': 5,
                           'TemplateBody': json.dumps(template, sort_keys=False),
                          })
        print formatted_parameters
        # get the form params
        result = c.create_stack(**formatted_parameters)
        return result

    @staticmethod
    def delete(stack_name):
        parameters = {'StackName': stack_name}
        c = heatclient
        result = c.delete_stack(**parameters)
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
