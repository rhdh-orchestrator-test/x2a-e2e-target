Migration Summary for ssh_profile:
  Total items: 8
  Completed: 8
  Pending: 0
  Missing: 0
  Errors: 0
  Write attempts: 1
  Validation attempts: 0

Final Validation Report:
All migration tasks have been completed successfully

Validation passed with warnings:
ansible-lint: Passed with 2 warning(s):
[MEDIUM] tasks/check_ssh_config.yml:18 [risky-shell-pipe] Shells that use pipes should set the pipefail option. (Task/Handler: Get PermitRootLogin setting from sshd_config)
[HIGH] tasks/check_ssh_config.yml:26 [command-instead-of-module] rpm used in place of yum or rpm_key module (Task/Handler: Check if openssh-server is installed)

==============================
Rule Hints (How to Fix):
==============================
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

Final checklist:
## Checklist: ssh_profile

### Recipes → Tasks
- [x] chef-and-ansible/tests/ssh_profile.rb → ./ansible/roles/ssh_profile/tasks/check_ssh_config.yml (complete) - Converted InSpec control to Ansible assertion task

### Attributes → Variables
- [x] chef-and-ansible/tests/ssh_profile.rb → ./ansible/roles/ssh_profile/vars/main.yml (complete) - Created vars file with security metadata from InSpec control

### Structure Files
- [x] N/A → ./ansible/roles/ssh_profile/meta/main.yml (complete) - Meta file already exists
- [x] N/A → ./ansible/roles/ssh_profile/tasks/main.yml (complete) - Created main tasks file that imports the check_ssh_config.yml tasks
- [x] N/A → ./ansible/roles/ssh_profile/defaults/main.yml (complete) - Created defaults file with role configuration variables
- [x] N/A → ./ansible/roles/ssh_profile/README.md (complete) - Created README with role documentation and security metadata
- [x] N/A → ansible/roles/ssh_profile/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] collection:ansible.posix → ./ansible/roles/ssh_profile/requirements.yml (complete) - Created requirements.yml with ansible.posix collection dependency


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 22.00s
    Tokens: 19328 in, 368 out
    Tools: aap_list_collections: 1, aap_search_collections: 3
    collections_found: 0
  PlanningAgent: 36.94s
    Tokens: 51455 in, 1750 out
    Tools: add_checklist_task: 7, list_checklist_tasks: 2, read_file: 1
  WriteAgent: 108.27s
    Tokens: 251395 in, 4406 out
    Tools: ansible_lint: 2, ansible_write: 7, list_checklist_tasks: 2, list_directory: 1, read_file: 3, update_checklist_task: 7, write_file: 1
    attempts: 1
    complete: True
    files_created: 8
    files_total: 8
  ValidationAgent: 8.98s
    collections_installed: 1
    collections_failed: 0
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False