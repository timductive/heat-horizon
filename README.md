heat-horizon (code name: thermal)
============

Heat horizon plugin: Thermal
Purpose of this plugin is to add heat-api capabilities to the openstack dashboard.
This plugin requires a working openstack install including heat and horizon.

To install, edit your horizon settings file:
- add ‘thermal’ to INSTALLED_APPS tuple;
- add ‘thermal’ to ‘dashboards’ key in HORIZON_CONFIG.
