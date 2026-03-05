✅ Migration Summary for chef_automate_deployment:
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
ansible-lint: Passed with 3 warning(s):
[HIGH] handlers/main.yml:1 [no-changed-when] Commands should not change things if nothing needs doing. (Task/Handler: Restart Chef Automate)
[HIGH] handlers/main.yml:6 [no-changed-when] Commands should not change things if nothing needs doing. (Task/Handler: Restart Chef Infra Server)
[HIGH] meta/main.yml:1 [meta-no-tags] Tags must contain lowercase letters and digits only., invalid: 'infra-server' ()

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

### Recipes → Tasks
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_deployment/tasks/deploy_automate.yml (complete) - Converted bash script to Ansible tasks with proper idempotence using creates parameters
- [x] setup-automate/deploy-chef-server.sh → ./ansible/roles/chef_automate_deployment/tasks/deploy_chef_server.yml (complete) - Converted bash script to Ansible tasks with proper idempotence using creates parameters

### Structure Files
- [x] N/A → ./ansible/roles/chef_automate_deployment/meta/main.yml (complete) - Created meta file with role metadata
- [x] N/A → ./ansible/roles/chef_automate_deployment/tasks/main.yml (complete) - Created main tasks file with conditional import of deploy_automate.yml or deploy_chef_server.yml
- [x] N/A → ./ansible/roles/chef_automate_deployment/defaults/main.yml (complete) - Created defaults file with all variables from the original bash scripts
- [x] N/A → ./ansible/roles/chef_automate_deployment/handlers/main.yml (complete) - Created handlers file with restart handlers for Chef Automate and Chef Infra Server
- [x] N/A → ./ansible/roles/chef_automate_deployment/README.md (complete) - Created README.md with role documentation, variables, and usage examples
- [x] N/A → ansible/roles/chef_automate_deployment/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] collection:ansible.builtin → ./ansible/roles/chef_automate_deployment/requirements.yml (complete) - Created requirements.yml with ansible.builtin collection
- [x] collection:ansible.posix → ./ansible/roles/chef_automate_deployment/requirements.yml (complete) - Added ansible.posix collection to requirements.yml


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 13.39s
    Tools: aap_list_collections: 1, aap_search_collections: 2
    collections_found: 0
  PlanningAgent: 36.01s
    Tools: add_checklist_task: 9, list_checklist_tasks: 2, list_directory: 1
  WriteAgent: 185.93s
    Tools: ansible_lint: 2, ansible_write: 16, get_checklist_summary: 1, list_checklist_tasks: 2, read_file: 2, update_checklist_task: 9, write_file: 2
    attempts: 1
    complete: True
    files_created: 10
    files_total: 10
  ValidationAgent: 52.55s
    collections_installed: 1
    collections_failed: 1
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False