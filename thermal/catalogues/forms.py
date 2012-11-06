from horizon import forms


class CataloguesForm(forms.Form):
    CATALOGUES = (('github-heatapi-template',
                   'Heat API GitHub Templates'),
                  ('aws-cloudformation-templates-us-east-1',
                   'AWS Cloudformation Templates (US East 1)'))
    catalogue = forms.ChoiceField(choices=CATALOGUES)
