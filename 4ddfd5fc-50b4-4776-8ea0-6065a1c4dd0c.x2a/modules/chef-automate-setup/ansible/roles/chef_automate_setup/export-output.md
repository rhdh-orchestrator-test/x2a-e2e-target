Migration Summary for chef_automate_setup:
  Total items: 15
  Completed: 15
  Pending: 0
  Missing: 0
  Errors: 0
  Write attempts: 1
  Validation attempts: 0

Final Validation Report:
All migration tasks have been completed successfully

Validation passed with warnings:
ansible-lint: Passed with 1 warning(s):
[HIGH] meta/main.yml:1 [meta-no-tags] Tags must contain lowercase letters and digits only., invalid: 'infra-server' ()

==============================
Rule Hints (How to Fix):
==============================
# meta-no-tags

Galaxy tags must use only lowercase letters and numbers.

## Problematic code

```yaml
galaxy_info:
  galaxy_tags: [MyTag#1, MyTag&^-]
```

## Correct code

```yaml
galaxy_info:
  galaxy_tags: [mytag1, mytag2]
```

Final checklist:
## Checklist: chef_automate_setup

### Recipes → Tasks
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_setup/tasks/system_config.yml (complete) - Converted system configuration tasks from bash script to Ansible tasks
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_setup/tasks/install_automate.yml (complete) - Converted Chef Automate installation tasks from bash script to Ansible tasks
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_setup/tasks/user_org_setup.yml (complete) - Converted user and organization setup tasks from bash script to Ansible tasks
- [x] setup-automate/deploy-chef-server.sh → ./ansible/roles/chef_automate_setup/tasks/install_chef_server.yml (complete) - Converted Chef Server installation tasks from bash script to Ansible tasks

### Attributes → Variables
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_setup/defaults/main.yml (complete) - Created defaults/main.yml with variables extracted from bash scripts

### Static Files
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_setup/files/deploy-automate.sh (complete) - Copied deploy-automate.sh script to files directory
- [x] setup-automate/deploy-chef-server.sh → ./ansible/roles/chef_automate_setup/files/deploy-chef-server.sh (complete) - Copied deploy-chef-server.sh script to files directory

### Structure Files
- [x] N/A → ./ansible/roles/chef_automate_setup/meta/main.yml (complete) - Created meta/main.yml with role metadata
- [x] N/A → ./ansible/roles/chef_automate_setup/tasks/main.yml (complete) - Created main tasks file that imports all task files
- [x] N/A → ./ansible/roles/chef_automate_setup/defaults/main.yml (complete) - Created defaults/main.yml with variables extracted from bash scripts
- [x] N/A → ./ansible/roles/chef_automate_setup/README.md (complete) - Created README.md with role documentation
- [x] N/A → ansible/roles/chef_automate_setup/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] collection:ansible.posix → ./ansible/roles/chef_automate_setup/requirements.yml (complete) - Created requirements.yml with required collections
- [x] collection:ansible.builtin → ./ansible/roles/chef_automate_setup/requirements.yml (complete) - Added ansible.builtin to requirements.yml
- [x] collection:community.general → ./ansible/roles/chef_automate_setup/requirements.yml (complete) - Added community.general to requirements.yml


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 14.11s
    Tokens: 18111 in, 514 out
    Tools: aap_list_collections: 1, aap_search_collections: 2
    collections_found: 0
  PlanningAgent: 49.47s
    Tokens: 98957 in, 2628 out
    Tools: add_checklist_task: 14, list_checklist_tasks: 2, list_directory: 1
  WriteAgent: 176.06s
    Tokens: 594338 in, 8138 out
    Tools: ansible_doc_lookup: 1, ansible_lint: 2, ansible_write: 12, copy_file: 2, get_checklist_summary: 1, list_checklist_tasks: 2, read_file: 3, update_checklist_task: 14, write_file: 1
    attempts: 1
    complete: True
    files_created: 15
    files_total: 15
  ValidationAgent: 14.65s
    collections_installed: 2
    collections_failed: 0
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False