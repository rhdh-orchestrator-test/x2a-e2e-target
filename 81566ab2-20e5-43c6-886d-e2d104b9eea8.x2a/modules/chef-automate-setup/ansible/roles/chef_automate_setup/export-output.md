Migration Summary for chef_automate_setup:
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
ansible-lint: Passed with 2 warning(s):
[MEDIUM] handlers/main.yml:2 [yaml] No new line character at the end of file ()
[HIGH] meta/main.yml:1 [meta-no-tags] Tags must contain lowercase letters and digits only., invalid: 'infra-server' ()

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
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_setup/tasks/deploy_automate.yml (complete) - Converted bash script to Ansible tasks with proper variables and idempotency
- [x] setup-automate/deploy-chef-server.sh → ./ansible/roles/chef_automate_setup/tasks/deploy_chef_server.yml (complete) - Converted bash script to Ansible tasks with proper variables and idempotency

### Structure Files
- [x] N/A → ./ansible/roles/chef_automate_setup/meta/main.yml (complete) - Created meta/main.yml with role metadata
- [x] N/A → ./ansible/roles/chef_automate_setup/tasks/main.yml (complete) - Created main tasks file that imports deploy_automate.yml and deploy_chef_server.yml with conditional execution
- [x] N/A → ./ansible/roles/chef_automate_setup/defaults/main.yml (complete) - Created defaults/main.yml with all variables from the bash scripts
- [x] N/A → ./ansible/roles/chef_automate_setup/handlers/main.yml (complete) - Created empty handlers file
- [x] N/A → ./ansible/roles/chef_automate_setup/README.md (complete) - Created comprehensive README.md with role documentation
- [x] N/A → ansible/roles/chef_automate_setup/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] collection:ansible.posix → ./ansible/roles/chef_automate_setup/requirements.yml (complete) - Added ansible.posix collection to requirements.yml
- [x] collection:ansible.builtin → ./ansible/roles/chef_automate_setup/requirements.yml (complete) - Added ansible.builtin collection to requirements.yml


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 13.25s
    Tokens: 17768 in, 455 out
    Tools: aap_list_collections: 1, aap_search_collections: 2
    collections_found: 0
  PlanningAgent: 36.28s
    Tokens: 64161 in, 1939 out
    Tools: add_checklist_task: 9, list_checklist_tasks: 2, list_directory: 1
  WriteAgent: 144.83s
    Tokens: 412586 in, 6496 out
    Tools: ansible_lint: 3, ansible_write: 10, list_checklist_tasks: 2, read_file: 2, update_checklist_task: 9, write_file: 3
    attempts: 1
    complete: True
    files_created: 10
    files_total: 10
  ValidationAgent: 9.13s
    collections_installed: 1
    collections_failed: 0
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False