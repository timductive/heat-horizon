from horizon import tables
from thermal.stacks.tables import ThermalStacksTable
from thermal.models import Stack

class IndexView(tables.DataTableView):
    table_class = ThermalStacksTable
    template_name = 'thermal/stacks/index.html'

    def get_data(self):
        return Stack.objects.all(self.request)
