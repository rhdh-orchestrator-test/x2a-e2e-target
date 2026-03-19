Migration Summary for chef_automate_deployment:
  Total items: 10
  Completed: 10
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
## Checklist: chef_automate_deployment

### Static Files
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_deployment/tasks/deploy_automate.yml (complete) - Converted bash script to Ansible tasks with variables for configuration
- [x] setup-automate/deploy-chef-server.sh → ./ansible/roles/chef_automate_deployment/tasks/deploy_chef_server.yml (complete) - Converted bash script to Ansible tasks with variables for configuration

### Structure Files
- [x] N/A → ./ansible/roles/chef_automate_deployment/meta/main.yml (complete) - Created meta/main.yml with role metadata
- [x] N/A → ./ansible/roles/chef_automate_deployment/tasks/main.yml (complete) - Created main tasks file that conditionally includes the appropriate deployment tasks based on deployment type
- [x] N/A → ./ansible/roles/chef_automate_deployment/defaults/main.yml (complete) - Created defaults file with all configurable variables from the original bash scripts
- [x] N/A → ./ansible/roles/chef_automate_deployment/README.md (complete) - Created comprehensive README.md with role documentation, variables, and usage examples
- [x] N/A → ./ansible/roles/chef_automate_deployment/handlers/main.yml (complete) - Created empty handlers file as no handlers are needed for this role
- [x] N/A → ansible/roles/chef_automate_deployment/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] collection:ansible.posix → ./ansible/roles/chef_automate_deployment/requirements.yml (complete) - Created requirements.yml with ansible.posix collection dependency
- [x] collection:ansible.builtin → ./ansible/roles/chef_automate_deployment/requirements.yml (complete) - Added ansible.builtin collection to requirements.yml


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 13.75s
    Tokens: 18447 in, 484 out
    Tools: aap_list_collections: 1, aap_search_collections: 2
    collections_found: 0
  PlanningAgent: 38.67s
    Tokens: 74588 in, 2140 out
    Tools: add_checklist_task: 10, list_checklist_tasks: 2, list_directory: 1
  WriteAgent: 174.04s
    Tokens: 520893 in, 7903 out
    Tools: ansible_lint: 3, ansible_write: 12, get_checklist_summary: 1, list_checklist_tasks: 2, read_file: 3, update_checklist_task: 9, write_file: 3
    attempts: 1
    complete: True
    files_created: 10
    files_total: 10
  ValidationAgent: 8.81s
    collections_installed: 1
    collections_failed: 0
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False