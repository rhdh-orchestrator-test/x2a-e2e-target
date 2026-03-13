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
ansible-lint: Passed with 5 warning(s):
[HIGH] meta/main.yml:1 [meta-no-tags] Tags must contain lowercase letters and digits only., invalid: 'infra-server' ()
[MEDIUM] tasks/deploy_automate.yml:6 [fqcn] You should use canonical module name `ansible.posix.sysctl` instead of `ansible.builtin.sysctl`. (Task/Handler: Set vm.max_map_count kernel parameter)
[MEDIUM] tasks/deploy_automate.yml:14 [fqcn] You should use canonical module name `ansible.posix.sysctl` instead of `ansible.builtin.sysctl`. (Task/Handler: Set vm.dirty_expire_centisecs kernel parameter)
[MEDIUM] tasks/deploy_chef_server.yml:6 [fqcn] You should use canonical module name `ansible.posix.sysctl` instead of `ansible.builtin.sysctl`. (Task/Handler: Set vm.max_map_count kernel parameter)
[MEDIUM] tasks/deploy_chef_server.yml:14 [fqcn] You should use canonical module name `ansible.posix.sysctl` instead of `ansible.builtin.sysctl`. (Task/Handler: Set vm.dirty_expire_centisecs kernel parameter)

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

# fqcn

Use fully-qualified collection names (FQCN) for all modules to avoid ambiguity.

## Problematic code

```yaml
- name: Create an SSH connection
  shell: ssh ssh_user@{{ ansible_ssh_host }}  # Missing FQCN
```

## Correct code

```yaml
# Option 1: Use ansible.builtin for built-in modules
- name: Create an SSH connection
  ansible.builtin.shell: ssh ssh_user@{{ ansible_ssh_host }}

# Option 2: Use ansible.legacy to allow local overrides
- name: Create an SSH connection
  ansible.legacy.shell: ssh ssh_user@{{ ansible_ssh_host }}
```

Tip: Use `ansible.builtin` for standard modules or `ansible.legacy` if you need local override compatibility.

Final checklist:
## Checklist: chef_automate_deployment

### Attributes → Variables
- [x] N/A → ./ansible/roles/chef_automate_deployment/vars/main.yml (complete) - Created vars/main.yml with Chef Automate and Chef Infra Server deployment variables

### Static Files
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_deployment/tasks/deploy_automate.yml (complete) - Created deploy_automate.yml task file to set up Chef Automate and Chef Infra Server
- [x] setup-automate/deploy-chef-server.sh → ./ansible/roles/chef_automate_deployment/tasks/deploy_chef_server.yml (complete) - Created deploy_chef_server.yml task file to set up Chef Infra Server only

### Structure Files
- [x] N/A → ./ansible/roles/chef_automate_deployment/meta/main.yml (complete) - Created meta/main.yml with role metadata
- [x] N/A → ./ansible/roles/chef_automate_deployment/tasks/main.yml (complete) - Created main.yml task file that conditionally includes deploy_automate.yml or deploy_chef_server.yml
- [x] N/A → ./ansible/roles/chef_automate_deployment/defaults/main.yml (complete) - Created defaults/main.yml with default variables for the role
- [x] N/A → ./ansible/roles/chef_automate_deployment/README.md (complete) - Created README.md with role documentation
- [x] N/A → ansible/roles/chef_automate_deployment/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] collection:ansible.builtin → ./ansible/roles/chef_automate_deployment/requirements.yml (complete) - Created requirements.yml with ansible.builtin collection dependency
- [x] collection:ansible.posix → ./ansible/roles/chef_automate_deployment/requirements.yml (complete) - Added ansible.posix collection to requirements.yml


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 14.14s
    Tokens: 18895 in, 486 out
    Tools: aap_list_collections: 1, aap_search_collections: 2
    collections_found: 0
  PlanningAgent: 37.74s
    Tokens: 65176 in, 1931 out
    Tools: add_checklist_task: 9, list_checklist_tasks: 2, list_directory: 1
  WriteAgent: 159.71s
    Tokens: 459490 in, 8922 out
    Tools: ansible_doc_lookup: 1, ansible_lint: 1, ansible_write: 13, get_checklist_summary: 1, list_checklist_tasks: 2, read_file: 2, update_checklist_task: 9, write_file: 1
    attempts: 1
    complete: True
    files_created: 10
    files_total: 10
  ValidationAgent: 11.63s
    collections_installed: 1
    collections_failed: 1
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False