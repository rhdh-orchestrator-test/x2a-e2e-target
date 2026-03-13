Migration Summary for chef_and_ansible:
  Total items: 14
  Completed: 14
  Pending: 0
  Missing: 0
  Errors: 0
  Write attempts: 1
  Validation attempts: 0

Final Validation Report:
All migration tasks have been completed successfully

Validation passed with warnings:
ansible-lint: Passed with 3 warning(s):
[HIGH] tasks/website_https.yml:51 [no-changed-when] Commands should not change things if nothing needs doing. (Task/Handler: Deactivate the default virtualhost)
[HIGH] tasks/website_https.yml:53 [no-changed-when] Commands should not change things if nothing needs doing. (Task/Handler: Activate the virtualhost)
[HIGH] tasks/website_https.yml:57 [no-changed-when] Commands should not change things if nothing needs doing. (Task/Handler: Activate SSL on Apache)

==============================
Rule Hints (How to Fix):
==============================
# no-changed-when

Commands should use `changed_when` to indicate when they actually change something.

## Problematic code

```yaml
- name: Does not handle any output or return codes
  ansible.builtin.command: cat {{ my_file | quote }}
```

## Correct code

```yaml
- name: Handle command output
  ansible.builtin.command: cat {{ my_file | quote }}
  register: my_output
  changed_when: my_output.rc != 0
```

Common patterns:
- `changed_when: false` - Task never changes anything
- `changed_when: true` - Task always changes something
- `changed_when: result.rc != 0` - Use command result to determine change

Final checklist:
## Checklist: chef_and_ansible

### Recipes → Tasks
- [x] chef-and-ansible/website_https.yml → ./ansible/roles/chef_and_ansible/tasks/website_https.yml (complete) - Converted to Ansible task file. Using community.crypto modules for SSL operations.
- [x] chef-and-ansible/poodle_fix.yml → ./ansible/roles/chef_and_ansible/tasks/poodle_fix.yml (complete) - Converted to Ansible task file. Using ansible.builtin.replace module to fix SSL POODLE vulnerability.

### Static Files
- [x] chef-and-ansible/index.html → ./ansible/roles/chef_and_ansible/files/index.html (complete) - Copied index.html file to Ansible role files directory.
- [x] chef-and-ansible/tests/website_https_verify.rb → ./ansible/roles/chef_and_ansible/tests/website_https_verify.yml (complete) - Converted InSpec test to Ansible test using ansible.builtin.assert, ansible.builtin.uri, and ansible.builtin.shell modules.
- [x] chef-and-ansible/tests/ssh_profile.rb → ./ansible/roles/chef_and_ansible/tests/ssh_profile.yml (complete) - Converted InSpec SSH profile test to Ansible test using ansible.builtin.assert, ansible.builtin.package_facts, and ansible.builtin.shell modules.
- [x] chef-and-ansible/kitchen.yml → ./ansible/roles/chef_and_ansible/molecule/default/molecule.yml (complete) - Converted Test Kitchen configuration to Molecule configuration with converge.yml and verify.yml files.

### Structure Files
- [x] N/A → ./ansible/roles/chef_and_ansible/meta/main.yml (complete) - Created meta/main.yml with role metadata.
- [x] N/A → ./ansible/roles/chef_and_ansible/tasks/main.yml (complete) - Created tasks/main.yml that imports website_https.yml and poodle_fix.yml tasks.
- [x] N/A → ./ansible/roles/chef_and_ansible/defaults/main.yml (complete) - Created defaults/main.yml with default variables for the role.
- [x] N/A → ./ansible/roles/chef_and_ansible/handlers/main.yml (complete) - Created handlers/main.yml with handlers for restarting apache and sshd services.
- [x] N/A → ansible/roles/chef_and_ansible/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] collection:ansible.posix → ./ansible/roles/chef_and_ansible/requirements.yml (complete) - Created requirements.yml with required collections: ansible.posix, community.crypto, and ansible.utils.
- [x] collection:community.crypto → ./ansible/roles/chef_and_ansible/requirements.yml (complete) - Added community.crypto collection to requirements.yml.
- [x] collection:ansible.utils → ./ansible/roles/chef_and_ansible/requirements.yml (complete) - Added ansible.utils collection to requirements.yml.


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 12.18s
    Tokens: 19832 in, 463 out
    Tools: aap_list_collections: 1, aap_search_collections: 2
    collections_found: 0
  PlanningAgent: 46.70s
    Tokens: 91138 in, 2551 out
    Tools: add_checklist_task: 13, list_checklist_tasks: 2
  WriteAgent: 185.25s
    Tokens: 639378 in, 8854 out
    Tools: ansible_lint: 2, ansible_write: 14, copy_file: 1, get_checklist_summary: 1, list_checklist_tasks: 2, read_file: 7, update_checklist_task: 13
    attempts: 1
    complete: True
    files_created: 14
    files_total: 14
  ValidationAgent: 16.77s
    collections_installed: 3
    collections_failed: 0
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False