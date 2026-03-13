Migration Summary for chef_automate_deployment:
  Total items: 14
  Completed: 14
  Pending: 0
  Missing: 0
  Errors: 0
  Write attempts: 1
  Validation attempts: 0

Final Validation Report:
All migration tasks have been completed successfully

Validation passed with warnings:
ansible-lint: Passed with 15 warning(s):
[MEDIUM] handlers/main.yml:1 [name] All names should start with an uppercase letter. (Task/Handler: reload sysctl)
[HIGH] handlers/main.yml:1 [no-changed-when] Commands should not change things if nothing needs doing. (Task/Handler: reload sysctl)
[LOW] handlers/main.yml:5 [ignore-errors] Use failed_when and specify error conditions instead of using ignore_errors. (Task/Handler: restart chef-automate)
[MEDIUM] handlers/main.yml:5 [name] All names should start with an uppercase letter. (Task/Handler: restart chef-automate)
[HIGH] handlers/main.yml:5 [no-changed-when] Commands should not change things if nothing needs doing. (Task/Handler: restart chef-automate)
[LOW] handlers/main.yml:10 [ignore-errors] Use failed_when and specify error conditions instead of using ignore_errors. (Task/Handler: restart chef-server)
[MEDIUM] handlers/main.yml:10 [name] All names should start with an uppercase letter. (Task/Handler: restart chef-server)
[HIGH] handlers/main.yml:10 [no-changed-when] Commands should not change things if nothing needs doing. (Task/Handler: restart chef-server)
[MEDIUM] tasks/create_users_orgs.yml:31 [no-handler] Tasks that run when changed should likely be handlers. (Task/Handler: Set permissions on user key file)
[MEDIUM] tasks/create_users_orgs.yml:39 [no-handler] Tasks that run when changed should likely be handlers. (Task/Handler: Set permissions on organization validator key file)
[MEDIUM] tasks/deploy_automate.yml:18 [no-handler] Tasks that run when changed should likely be handlers. (Task/Handler: Wait for Chef Automate deployment to complete)
[MEDIUM] tasks/deploy_chef_server.yml:18 [no-handler] Tasks that run when changed should likely be handlers. (Task/Handler: Wait for Chef Infra Server deployment to complete)
[HIGH] tasks/install_cli.yml:8 [command-instead-of-module] curl used in place of get_url or uri module (Task/Handler: Download and extract Chef Automate CLI)
[MEDIUM] tasks/install_cli.yml:8 [risky-shell-pipe] Shells that use pipes should set the pipefail option. (Task/Handler: Download and extract Chef Automate CLI)
[MEDIUM] tasks/install_cli.yml:20 [no-handler] Tasks that run when changed should likely be handlers. (Task/Handler: Make Chef Automate CLI executable)

==============================
Rule Hints (How to Fix):
==============================
# name

All tasks and plays should be named with proper casing (uppercase first letter).

## Problematic code

```yaml
- name: create placeholder file
  ansible.builtin.command: touch /tmp/.placeholder
```

## Correct code

```yaml
- name: Create placeholder file
  ansible.builtin.command: touch /tmp/.placeholder
```

**Tip:** All task names within a play should be unique for reliable debugging with `--start-at-task`.

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

# ignore-errors

Use conditional ignoring, register errors, or define specific failure conditions instead of blindly ignoring all errors.

## Problematic code

```yaml
- name: Run apt-get update
  ansible.builtin.command: apt-get update
  ignore_errors: true # Ignores all errors
```

## Correct code

```yaml
# Option 1: Ignore only in check mode
- name: Run apt-get update
  ansible.builtin.command: apt-get update
  ignore_errors: "{{ ansible_check_mode }}"

# Option 2: Register and handle errors
- name: Run apt-get update
  ansible.builtin.command: apt-get update
  ignore_errors: true
  register: update_result

# Option 3: Define specific failure conditions
- name: Disable apport
  lineinfile:
    line: "enabled=0"
    dest: /etc/default/apport
  register: result
  failed_when: result.rc != 0 and result.rc != 257
```

# no-handler

Tasks with `when: result.changed` conditions should use handlers with `notify` instead.

## Problematic code

```yaml
- name: Register result of a task
  ansible.builtin.copy:
    dest: "/tmp/placeholder"
    content: "Ansible made this!"
    mode: 0600
  register: result

- name: Second command to run
  ansible.builtin.debug:
    msg: The placeholder file was modified!
  when: result.changed
```

## Correct code

```yaml
- name: Register result of a task
  ansible.builtin.copy:
    dest: "/tmp/placeholder"
    content: "Ansible made this!"
    mode: 0600
  notify:
    - Second command to run

handlers:
  - name: Second command to run
    ansible.builtin.debug:
      msg: The placeholder file was modified!
```

**Tip:** Handlers run only once at the end of a play, even if notified multiple times.

# command-instead-of-module

Use specific ansible modules instead of generic command/shell modules when available.

## Problematic code

```yaml
- name: Run apt-get update
  ansible.builtin.command: apt-get update
```

## Correct code

```yaml
- name: Run apt-get update
  ansible.builtin.apt:
    update_cache: true
```

Tip: Check the ansible-lint rule source for the full list of commands that have dedicated modules.

# risky-shell-pipe

Always set `pipefail` when piping shell commands to avoid hiding failures in earlier commands.

## Problematic code

```yaml
- name: Pipeline without pipefail
  ansible.builtin.shell: false | cat
```

## Correct code

```yaml
- name: Pipeline with pipefail
  ansible.builtin.shell:
    cmd: set -o pipefail && false | cat
    executable: /bin/bash

- name: Pipeline with pipefail, multi-line
  ansible.builtin.shell:
    cmd: |
      set -o pipefail
      false | cat
    executable: /bin/bash
```

**Tip**: This rule does not apply to PowerShell (pwsh executable).

Final checklist:
## Checklist: chef_automate_deployment

### Recipes → Tasks
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_deployment/tasks/system_config.yml (complete) - Created system configuration tasks to set hostname and kernel parameters
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_deployment/tasks/install_cli.yml (complete) - Created tasks to download and install Chef Automate CLI
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_deployment/tasks/deploy_automate.yml (complete) - Created tasks to deploy Chef Automate and Chef Infra Server
- [x] setup-automate/deploy-chef-server.sh → ./ansible/roles/chef_automate_deployment/tasks/deploy_chef_server.yml (complete) - Created tasks to deploy Chef Infra Server only
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_deployment/tasks/create_users_orgs.yml (complete) - Created tasks to create Chef users and organizations
- [x] N/A → ./ansible/roles/chef_automate_deployment/tasks/verify.yml (complete) - Created verification tasks to check deployment status

### Attributes → Variables
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_deployment/defaults/main.yml (complete) - Created default variables from Chef Automate deployment scripts

### Static Files
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_automate_deployment/files/deploy-automate.sh (complete) - Copied original Chef Automate deployment script
- [x] setup-automate/deploy-chef-server.sh → ./ansible/roles/chef_automate_deployment/files/deploy-chef-server.sh (complete) - Copied original Chef Server deployment script

### Structure Files
- [x] N/A → ./ansible/roles/chef_automate_deployment/meta/main.yml (complete) - Meta file already exists
- [x] N/A → ./ansible/roles/chef_automate_deployment/tasks/main.yml (complete) - Created main tasks file to import all task modules
- [x] N/A → ./ansible/roles/chef_automate_deployment/defaults/main.yml (complete) - Defaults file already created
- [x] N/A → ./ansible/roles/chef_automate_deployment/handlers/main.yml (complete) - Created handlers for restarting services and reloading sysctl
- [x] N/A → ansible/roles/chef_automate_deployment/meta/main.yml (complete)


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 29.10s
    Tokens: 29431 in, 580 out
    Tools: aap_list_collections: 1, aap_search_collections: 4
    collections_found: 0
  PlanningAgent: 50.32s
    Tokens: 101969 in, 2591 out
    Tools: add_checklist_task: 14, list_checklist_tasks: 2, list_directory: 1
  WriteAgent: 330.43s
    Tokens: 431936 in, 5976 out
    Tools: ansible_lint: 3, ansible_write: 9, get_checklist_summary: 1, list_checklist_tasks: 3, list_directory: 1, read_file: 5, update_checklist_task: 2
    attempts: 1
    complete: True
    files_created: 14
    files_total: 14
  ValidationAgent: 5.60s
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False