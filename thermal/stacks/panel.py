from django.utils.translation import ugettext_lazy as _

import horizon

from thermal import dashboard


class Stacks(horizon.Panel):
    name = _("Stacks")
    slug = "stacks"


dashboard.Thermal.register(Stacks)
