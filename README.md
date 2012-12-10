heat-horizon (code name: thermal)
============

Heat horizon plugin: Thermal
Purpose of this plugin is to add heat-api capabilities to the openstack dashboard.
This plugin requires a working openstack install including heat and horizon.

Important:
This dashboard is developed on the master branch of openstack dashboard and the master branch of heat.
Errors you will recieve if you are using older code include, but are not limited to:
- Invalid service catalog service: orchestration
- ImportError: No module named api.base

To install
- install openstack including horizon, python-heatclient and heat
- heat-horizon$ `sudo ./setup.py install`

Then, edit your openstack_dashboard settings file:
- add ‘thermal’ to INSTALLED_APPS tuple;
- add ‘thermal’ to ‘dashboards’ key in the HORIZON_CONFIG dictionary.

Troubleshooting:

