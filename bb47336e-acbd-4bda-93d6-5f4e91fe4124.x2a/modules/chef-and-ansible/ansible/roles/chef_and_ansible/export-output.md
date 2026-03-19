Migration Summary for chef_and_ansible:
  Total items: 13
  Completed: 13
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
- [x] chef-and-ansible/website_https.yml → ./ansible/roles/chef_and_ansible/tasks/website_https.yml (complete) - Converted website_https.yml to Ansible task format with FQCN module names
- [x] chef-and-ansible/poodle_fix.yml → ./ansible/roles/chef_and_ansible/tasks/poodle_fix.yml (complete) - Converted poodle_fix.yml to Ansible task format with FQCN module names

### Static Files
- [x] chef-and-ansible/tests/website_https_verify.rb → ./ansible/roles/chef_and_ansible/tests/website_https_verify.yml (complete) - Converted InSpec test to Ansible test format
- [x] chef-and-ansible/tests/ssh_profile.rb → ./ansible/roles/chef_and_ansible/tests/ssh_profile.yml (complete) - Converted InSpec SSH profile test to Ansible test format
- [x] chef-and-ansible/index.html → ./ansible/roles/chef_and_ansible/files/index.html (complete) - Copied index.html to files directory

### Structure Files
- [x] N/A → ./ansible/roles/chef_and_ansible/meta/main.yml (complete) - Created meta/main.yml with role metadata
- [x] N/A → ./ansible/roles/chef_and_ansible/tasks/main.yml (complete) - Created main tasks file that imports website_https.yml and poodle_fix.yml
- [x] N/A → ./ansible/roles/chef_and_ansible/defaults/main.yml (complete) - Created defaults/main.yml with variables from the original playbooks
- [x] N/A → ./ansible/roles/chef_and_ansible/handlers/main.yml (complete) - Created handlers/main.yml with service restart handlers
- [x] N/A → ansible/roles/chef_and_ansible/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] collection:ansible.posix → ./ansible/roles/chef_and_ansible/requirements.yml (complete) - Created requirements.yml with ansible.posix collection
- [x] collection:community.crypto → ./ansible/roles/chef_and_ansible/requirements.yml (complete) - Added community.crypto collection to requirements.yml
- [x] collection:ansible.utils → ./ansible/roles/chef_and_ansible/requirements.yml (complete) - Added ansible.utils collection to requirements.yml


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 12.03s
    Tokens: 15081 in, 451 out
    Tools: aap_list_collections: 1, aap_search_collections: 2
    collections_found: 0
  PlanningAgent: 45.03s
    Tokens: 80415 in, 2459 out
    Tools: add_checklist_task: 12, list_checklist_tasks: 2, list_directory: 2
  WriteAgent: 133.76s
    Tokens: 421747 in, 6423 out
    Tools: ansible_lint: 1, ansible_write: 7, copy_file: 1, get_checklist_summary: 1, list_checklist_tasks: 2, read_file: 5, update_checklist_task: 12, write_file: 2
    attempts: 1
    complete: True
    files_created: 13
    files_total: 13
  ValidationAgent: 17.75s
    collections_installed: 3
    collections_failed: 0
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False