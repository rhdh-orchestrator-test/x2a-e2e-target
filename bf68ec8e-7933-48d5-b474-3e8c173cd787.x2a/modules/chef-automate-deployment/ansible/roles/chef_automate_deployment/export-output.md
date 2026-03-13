Migration Summary for chef_automate_deployment:
  Total items: 11
  Completed: 11
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

### Attributes → Variables
- [x] N/A → ./ansible/roles/chef_automate_deployment/vars/main.yml (complete) - Created vars/main.yml with Chef Automate deployment variables

### Static Files
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_deployment/tasks/deploy_automate.yml (complete) - Converted deploy-automate.sh to Ansible tasks
- [x] setup-automate/deploy-chef-server.sh → ./ansible/roles/chef_automate_deployment/tasks/deploy_chef_server.yml (complete) - Converted deploy-chef-server.sh to Ansible tasks

### Structure Files
- [x] N/A → ./ansible/roles/chef_automate_deployment/meta/main.yml (complete) - Created meta/main.yml with role metadata
- [x] N/A → ./ansible/roles/chef_automate_deployment/tasks/main.yml (complete) - Created main tasks file that includes deploy_automate.yml or deploy_chef_server.yml based on deployment_type variable
- [x] N/A → ./ansible/roles/chef_automate_deployment/defaults/main.yml (complete) - Created defaults/main.yml with default variables
- [x] N/A → ./ansible/roles/chef_automate_deployment/README.md (complete) - Created README.md with role documentation
- [x] N/A → ansible/roles/chef_automate_deployment/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] collection:ansible.posix → ./ansible/roles/chef_automate_deployment/requirements.yml (complete) - Created requirements.yml with required collections
- [x] collection:ansible.builtin → ./ansible/roles/chef_automate_deployment/requirements.yml (complete) - Added ansible.builtin collection to requirements.yml
- [x] collection:community.general → ./ansible/roles/chef_automate_deployment/requirements.yml (complete) - Added community.general collection to requirements.yml


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 15.68s
    Tokens: 19947 in, 508 out
    Tools: aap_list_collections: 1, aap_search_collections: 2
    collections_found: 0
  PlanningAgent: 39.42s
    Tokens: 73306 in, 2015 out
    Tools: add_checklist_task: 10, list_checklist_tasks: 2, list_directory: 1
  WriteAgent: 153.71s
    Tokens: 448444 in, 7582 out
    Tools: ansible_doc_lookup: 1, ansible_lint: 2, ansible_write: 10, get_checklist_summary: 1, list_checklist_tasks: 2, read_file: 3, update_checklist_task: 10, write_file: 1
    attempts: 1
    complete: True
    files_created: 11
    files_total: 11
  ValidationAgent: 15.78s
    collections_installed: 2
    collections_failed: 0
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False