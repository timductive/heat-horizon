from django.utils.translation import ugettext_lazy as _

import horizon


class Thermal(horizon.Dashboard):
    name = _("Heat")
    slug = "thermal"
    panels = ('stacks', )  # Add your panels here.
    default_panel = 'stacks'  # the slug of the dashboard's default panel.


horizon.register(Thermal)
