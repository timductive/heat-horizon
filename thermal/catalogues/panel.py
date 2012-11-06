from django.utils.translation import ugettext_lazy as _

import horizon

from thermal import dashboard


class Catalogues(horizon.Panel):
    name = _("Catalogues")
    slug = "catalogues"


dashboard.Thermal.register(Catalogues)
