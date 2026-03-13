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
[MEDIUM] handlers/main.yml:3 [yaml] No new line character at the end of file ()

==============================
Rule Hints (How to Fix):
==============================
# yaml

Checks YAML syntax for indentation and formatting issues.

## Common indentation issues

### Problematic code

```yaml
# Incorrect indentation
- name: Configure service
  service:
  name: nginx  # <- Should be indented under service
  state: started
```

```yaml
# Inconsistent indentation
- name: Install packages
  apt:
    name: nginx
      state: present  # <- Too much indentation
```

```yaml
# Comment indentation
- name: Task
  debug:
    msg: "test"
      # <- Comment indented incorrectly
```

### Correct code

```yaml
# Correct indentation
- name: Configure service
  service:
    name: nginx  # <- Properly indented
    state: started
```

```yaml
# Consistent indentation
- name: Install packages
  apt:
    name: nginx
    state: present  # <- Aligned with name
```

```yaml
# Comment indentation
- name: Task
  debug:
    msg: "test"
  # <- Comment at correct level
```

## Other common issues

### Octal values

```yaml
# Problematic
permissions: 0777  # <- yaml[octal-values]

# Correct
permissions: "0777"  # <- Quote octal values
```

### Duplicate keys

```yaml
# Problematic
foo: value1
foo: value2  # <- yaml[key-duplicates]

# Correct
foo: value2  # <- Use unique keys
```

Final checklist:
## Checklist: chef_automate_deployment

### Recipes → Tasks
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_deployment/tasks/deploy_automate.yml (complete) - Converted bash script to Ansible tasks
- [x] setup-automate/deploy-chef-server.sh → ./ansible/roles/chef_automate_deployment/tasks/deploy_chef_server.yml (complete) - Converted bash script to Ansible tasks

### Attributes → Variables
- [x] N/A → ./ansible/roles/chef_automate_deployment/vars/main.yml (complete) - Created vars file with Chef Automate deployment variables

### Structure Files
- [x] N/A → ./ansible/roles/chef_automate_deployment/meta/main.yml (complete) - Created meta file with role metadata
- [x] N/A → ./ansible/roles/chef_automate_deployment/tasks/main.yml (complete) - Created main tasks file to import task files
- [x] N/A → ./ansible/roles/chef_automate_deployment/defaults/main.yml (complete) - Created defaults file with configurable variables
- [x] N/A → ./ansible/roles/chef_automate_deployment/handlers/main.yml (complete) - Created empty handlers file
- [x] N/A → ansible/roles/chef_automate_deployment/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] collection:ansible.posix → ./ansible/roles/chef_automate_deployment/requirements.yml (complete) - Added required collections to requirements.yml
- [x] collection:community.general → ./ansible/roles/chef_automate_deployment/requirements.yml (complete) - Added required collections to requirements.yml


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 15.62s
    Tokens: 24043 in, 565 out
    Tools: aap_list_collections: 1, aap_search_collections: 3
    collections_found: 0
  PlanningAgent: 37.87s
    Tokens: 65601 in, 1920 out
    Tools: add_checklist_task: 9, list_checklist_tasks: 2, list_directory: 1
  WriteAgent: 142.52s
    Tokens: 392487 in, 6596 out
    Tools: ansible_doc_lookup: 1, ansible_lint: 2, ansible_write: 11, list_checklist_tasks: 2, read_file: 3, update_checklist_task: 9
    attempts: 1
    complete: True
    files_created: 10
    files_total: 10
  ValidationAgent: 25.16s
    collections_installed: 2
    collections_failed: 0
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False