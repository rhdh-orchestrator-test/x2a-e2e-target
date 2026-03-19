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

All validations passed

Final checklist:
## Checklist: chef_and_ansible

### Recipes → Tasks
- [x] chef-and-ansible/website_https.yml → ./ansible/roles/chef_and_ansible/tasks/website_https.yml (complete) - Converted Ansible playbook to task file with proper FQCN module names
- [x] chef-and-ansible/poodle_fix.yml → ./ansible/roles/chef_and_ansible/tasks/poodle_fix.yml (complete) - Converted Ansible playbook to task file with proper FQCN module names

### Static Files
- [x] chef-and-ansible/index.html → ./ansible/roles/chef_and_ansible/files/index.html (complete) - Copied index.html file to Ansible role files directory
- [x] chef-and-ansible/tests/website_https_verify.rb → ./ansible/roles/chef_and_ansible/tests/website_https_verify.yml (complete) - Converted InSpec test to Ansible test format
- [x] chef-and-ansible/tests/ssh_profile.rb → ./ansible/roles/chef_and_ansible/tests/ssh_profile.yml (complete) - Converted InSpec SSH profile test to Ansible test format
- [x] chef-and-ansible/kitchen.yml → ./ansible/roles/chef_and_ansible/molecule/default/molecule.yml (complete) - Converted Test Kitchen configuration to Molecule format

### Structure Files
- [x] N/A → ./ansible/roles/chef_and_ansible/meta/main.yml (complete) - Created meta/main.yml with role metadata
- [x] N/A → ./ansible/roles/chef_and_ansible/tasks/main.yml (complete) - Created main tasks file that imports website_https.yml and poodle_fix.yml
- [x] N/A → ./ansible/roles/chef_and_ansible/defaults/main.yml (complete) - Created defaults/main.yml with role variables
- [x] N/A → ./ansible/roles/chef_and_ansible/handlers/main.yml (complete) - Created handlers/main.yml with apache and sshd restart handlers
- [x] N/A → ansible/roles/chef_and_ansible/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] collection:ansible.posix → ./ansible/roles/chef_and_ansible/requirements.yml (complete) - Added required collections to requirements.yml
- [x] collection:community.crypto → ./ansible/roles/chef_and_ansible/requirements.yml (complete) - Added required collections to requirements.yml
- [x] collection:community.general → ./ansible/roles/chef_and_ansible/requirements.yml (complete) - Added required collections to requirements.yml


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 13.42s
    Tokens: 19596 in, 472 out
    Tools: aap_list_collections: 1, aap_search_collections: 2
    collections_found: 0
  PlanningAgent: 47.91s
    Tokens: 103978 in, 2545 out
    Tools: add_checklist_task: 13, list_checklist_tasks: 2, list_directory: 2
  WriteAgent: 138.93s
    Tokens: 509525 in, 6564 out
    Tools: ansible_lint: 1, ansible_write: 7, get_checklist_summary: 1, list_checklist_tasks: 2, read_file: 6, update_checklist_task: 13, write_file: 4
    attempts: 1
    complete: True
    files_created: 14
    files_total: 14
  ValidationAgent: 17.26s
    collections_installed: 3
    collections_failed: 0
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False