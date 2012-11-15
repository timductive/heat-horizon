from django.utils.translation import ugettext_lazy as _

import horizon

from thermal import dashboard


class Designer(horizon.Panel):
    name = _("Designer")
    slug = "designer"


dashboard.Thermal.register(Designer)
