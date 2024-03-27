===============================================
Ansible Plugin Builder Collection Release Notes
===============================================

.. contents:: Topics


v1.0.0
======

Release Summary
---------------

Release 1.0.0 with content generation roles

Minor Changes
-------------

- Add requires_ansible to manifest (https://github.com/ansible-community/ansible.content_builder/pull/76).
- Add support for RM generating scaffolding tool using OpenApi based swagger JSON file
- Adds a task to the module_openapi_cloud role to remove unused imports from the generated module.
- Apply the latest changes needed for amazon.cloud 0.3.0 release.
- Change variable names that are used in the plugin files to match the ones in vars file.
- Fix for use folder attribute for host and dc module only
- Generate action_groups for the vmware.vmware_rest collection (https://github.com/ansible-community/ansible.content_builder/issues/75).
- Get cloud formation resource type from modules.yaml.
- Integrate cloud content generator with content_builder (https://github.com/ansible-community/ansible.content_builder/pull/43).
- Update netconf supported network_module template.
- Update the vSphere requirements for generated vmware.vmware_rest modules (https://github.com/ansible-community/ansible.content_builder/pull/73).
- Use folder attribute for host and dc module only (https://github.com/ansible-community/ansible.content_builder/pull/79).
- generate_cloud_modules should keep entries for files not part of ``plugins/*`` when generating ``tests/sanity/ignore-*.txt`` files.
- vmware.vmware_rest - Add new resource mappings (https://github.com/ansible-community/ansible.content_builder/pull/74).
- vmware.vmware_rest - Fix incorrectly sorted imports (https://github.com/ansible-community/ansible.content_builder/pull/74).

Bugfixes
--------

- Change galaxy.yaml to galaxy.yaml
- Do not fail if plugin content type is undefined.
- To fix the doc_generator issue for secbuity RM builder using OpenAPI JSON file.
- Updates for roles.
- https://github.com/ansible-community/ansible.content_builder/issues/28
- https://github.com/ansible-community/ansible.content_builder/issues/29
- remove unnecessary q import (https://github.com/ansible-community/ansible.content_builder/pull/60).

Documentation Changes
---------------------

- Add dependency installation in README.
- Add resource module development doc.
- Minor updates to the README.
