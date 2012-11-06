CATALOGUES = {
  ## Valid types are github and aws
  ## template name will be appended to base to download the template contents
  'github-heatapi-template': {
    'type': 'github',
    'feed': 'https://api.github.com/repos/heat-api/heat/contents/templates',
    'base': 'https://raw.github.com/heat-api/heat/master/templates/',
  },
  'aws-cloudformation-templates-us-east-1': {
    'type': 'aws',
    'feed': 'https://s3.amazonaws.com/cloudformation-templates-us-east-1/',
    'base': 'https://s3.amazonaws.com/cloudformation-templates-us-east-1/',
  },
}
