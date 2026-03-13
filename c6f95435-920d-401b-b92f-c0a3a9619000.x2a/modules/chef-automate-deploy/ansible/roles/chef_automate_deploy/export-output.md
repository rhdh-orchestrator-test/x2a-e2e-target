Migration Summary for chef_automate_deploy:
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
ansible-lint: Passed with 8 warning(s):
[MEDIUM] handlers/main.yml:5 [yaml] No new line character at the end of file ()
[HIGH] meta/main.yml:1 [meta-no-tags] Tags must contain lowercase letters and digits only., invalid: 'infra-server' ()
[MEDIUM] tasks/deploy_automate.yml:5 [fqcn] Use FQCN for module actions, such `ansible.posix.sysctl`. (Action `sysctl` is not FQCN.)
[MEDIUM] tasks/deploy_automate.yml:11 [fqcn] Use FQCN for module actions, such `ansible.posix.sysctl`. (Action `sysctl` is not FQCN.)
[VERY_HIGH] tasks/deploy_automate.yml:21 [inline-env-var] Command module does not accept setting environment variables inline. (Task/Handler: Unzip Chef Automate CLI)
[MEDIUM] tasks/deploy_chef_server.yml:5 [fqcn] Use FQCN for module actions, such `ansible.posix.sysctl`. (Action `sysctl` is not FQCN.)
[MEDIUM] tasks/deploy_chef_server.yml:11 [fqcn] Use FQCN for module actions, such `ansible.posix.sysctl`. (Action `sysctl` is not FQCN.)
[VERY_HIGH] tasks/deploy_chef_server.yml:21 [inline-env-var] Command module does not accept setting environment variables inline. (Task/Handler: Unzip Chef Automate CLI)

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

# inline-env-var

Do not set environment variables in the `ansible.builtin.command` module.

## Problematic code

```yaml
- name: Set environment variable
  ansible.builtin.command: MY_ENV_VAR=my_value some_command
```

## Correct code (Option 1: Use environment keyword)

```yaml
- name: Set environment variable
  ansible.builtin.command: some_command
  environment:
    MY_ENV_VAR: my_value
```

## Correct code (Option 2: Use shell module)

```yaml
- name: Set environment variable
  ansible.builtin.shell: MY_ENV_VAR=my_value some_command
```

Tip: Prefer `environment` keyword with `command` module for clarity.

Final checklist:
## Checklist: chef_automate_deploy

### Recipes → Tasks
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_deploy/tasks/deploy_automate.yml (complete) - Created deploy_automate.yml with tasks to set hostname, configure kernel parameters, download and install Chef Automate CLI, deploy Chef Automate and Chef Infra Server, and create initial user and organization.
- [x] setup-automate/deploy-chef-server.sh → ./ansible/roles/chef_automate_deploy/tasks/deploy_chef_server.yml (complete) - Created deploy_chef_server.yml with tasks to set hostname, configure kernel parameters, download and install Chef Automate CLI, deploy Chef Infra Server only, and create initial user and organization.

### Structure Files
- [x] N/A → ./ansible/roles/chef_automate_deploy/meta/main.yml (complete) - Created meta/main.yml with role metadata including description, license, platform support, and tags.
- [x] N/A → ./ansible/roles/chef_automate_deploy/tasks/main.yml (complete) - Created main.yml that conditionally includes either deploy_automate.yml or deploy_chef_server.yml based on the chef_automate_deploy_full variable.
- [x] N/A → ./ansible/roles/chef_automate_deploy/defaults/main.yml (complete) - Created defaults/main.yml with all the necessary variables for Chef Automate and Chef Infra Server deployment, including hostname, user details, and organization settings.
- [x] N/A → ./ansible/roles/chef_automate_deploy/handlers/main.yml (complete) - Created handlers/main.yml file (empty as no handlers are needed for this role).
- [x] N/A → ./ansible/roles/chef_automate_deploy/README.md (complete) - Created README.md with role documentation including requirements, variables, dependencies, example playbook, and license information.
- [x] N/A → ansible/roles/chef_automate_deploy/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] collection:ansible.builtin → ./ansible/roles/chef_automate_deploy/requirements.yml (complete) - Added ansible.builtin collection to requirements.yml.
- [x] collection:ansible.posix → ./ansible/roles/chef_automate_deploy/requirements.yml (complete) - Added ansible.posix collection to requirements.yml.


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 14.33s
    Tokens: 18612 in, 475 out
    Tools: aap_list_collections: 1, aap_search_collections: 2
    collections_found: 0
  PlanningAgent: 40.72s
    Tokens: 64502 in, 2005 out
    Tools: add_checklist_task: 9, list_checklist_tasks: 2, list_directory: 1
  WriteAgent: 187.76s
    Tokens: 536176 in, 10042 out
    Tools: ansible_doc_lookup: 1, ansible_lint: 2, ansible_write: 14, list_checklist_tasks: 2, read_file: 2, update_checklist_task: 9, write_file: 2
    attempts: 1
    complete: True
    files_created: 10
    files_total: 10
  ValidationAgent: 10.97s
    collections_installed: 1
    collections_failed: 1
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False