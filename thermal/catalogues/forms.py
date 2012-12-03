from horizon import forms

from thermal import CATALOGUES


class CataloguesForm(forms.Form):
    catalogue = forms.ChoiceField(choices= \
                    map(lambda x: (x, CATALOGUES[x]['name']),
                        CATALOGUES))
