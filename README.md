heat-horizon (code name: thermal)
============

Heat horizon plugin: Thermal
Purpose of this plugin is to add heat-api capabilities to the openstack dashboard.
This plugin requires a working openstack install including heat and horizon.

To install
- install openstack including horizon and heat
- `sudo ./setup.py install`

Then, edit your horizon settings file:
- add ‘thermal’ to INSTALLED_APPS tuple;
- add ‘thermal’ to ‘dashboards’ key in HORIZON_CONFIG.

Know issues: 
1. Invalid service catalog service: heat
    - in thermal/api.py update the url_for call from url_for(request, 'heat') to url_for(request, 'orchestration')
2. ImportError: No module named api.base
    - update thermal/api.py to import from openstack_dashboard.api.base instead of horizon.api.base
