Migration Summary for chef_inspec_tests:
  Total items: 11
  Completed: 11
  Pending: 0
  Missing: 0
  Errors: 0
  Write attempts: 1
  Validation attempts: 0

Final Validation Report:
All migration tasks have been completed successfully

All validations passed

Final checklist:
## Checklist: chef_inspec_tests

### Recipes → Tasks
- [x] chef-and-ansible/tests/ssh_profile.rb → ./ansible/roles/chef_inspec_tests/tasks/ssh_security_test.yml (complete) - Converted InSpec SSH security test to Ansible tasks that check SSH configuration and package status
- [x] chef-and-ansible/tests/website_https_verify.rb → ./ansible/roles/chef_inspec_tests/tasks/website_https_test.yml (complete) - Converted InSpec HTTPS website test to Ansible tasks that check port, website response, and SSL/TLS protocols

### Static Files
- [x] chef-and-ansible/tests/ssh_profile.rb → ./ansible/roles/chef_inspec_tests/tests/ssh_security.yml (complete) - Created Ansible test playbook equivalent to the InSpec SSH security test
- [x] chef-and-ansible/tests/website_https_verify.rb → ./ansible/roles/chef_inspec_tests/tests/website_https_verify.yml (complete) - Created Ansible test playbook equivalent to the InSpec HTTPS website verification test

### Structure Files
- [x] N/A → ./ansible/roles/chef_inspec_tests/meta/main.yml (complete) - Created meta/main.yml with role metadata
- [x] N/A → ./ansible/roles/chef_inspec_tests/tasks/main.yml (complete) - Created main tasks file that imports the SSH and HTTPS test tasks
- [x] N/A → ./ansible/roles/chef_inspec_tests/defaults/main.yml (complete) - Created defaults/main.yml with variables for the tests
- [x] N/A → ansible/roles/chef_inspec_tests/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] collection:ansible.posix → ./ansible/roles/chef_inspec_tests/requirements.yml (complete) - Created requirements.yml with required collections
- [x] collection:community.general → ./ansible/roles/chef_inspec_tests/requirements.yml (complete) - Added community.general collection to requirements.yml
- [x] collection:community.crypto → ./ansible/roles/chef_inspec_tests/requirements.yml (complete) - Added community.crypto collection to requirements.yml


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 13.10s
    Tokens: 16940 in, 468 out
    Tools: aap_list_collections: 1, aap_search_collections: 2
    collections_found: 0
  PlanningAgent: 39.21s
    Tokens: 70363 in, 1983 out
    Tools: add_checklist_task: 10, list_checklist_tasks: 2, list_directory: 1
  WriteAgent: 132.66s
    Tokens: 368002 in, 6895 out
    Tools: ansible_lint: 1, ansible_write: 10, get_checklist_summary: 1, list_checklist_tasks: 2, read_file: 2, update_checklist_task: 10
    attempts: 1
    complete: True
    files_created: 11
    files_total: 11
  ValidationAgent: 16.10s
    collections_installed: 3
    collections_failed: 0
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False