Migration Summary for chef_deployment:
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
ansible-lint: Passed with 2 warning(s):
[MEDIUM] handlers/main.yml:3 [yaml] No new line character at the end of file ()
[MEDIUM] vars/main.yml:3 [yaml] No new line character at the end of file ()

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
## Checklist: chef_deployment

### Attributes → Variables
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_deployment/defaults/main.yml (complete) - Created defaults/main.yml with variables for Chef deployment including hostname, user details, organization details, and deployment type flags.

### Static Files
- [x] setup-automate/deploy-automate.sh → ./ansible/roles/chef_deployment/tasks/deploy_automate.yml (complete) - Created deploy_automate.yml with tasks to set hostname, configure sysctl parameters, download and deploy Chef Automate with Infra Server, and create Chef user and organization.
- [x] setup-automate/deploy-chef-server.sh → ./ansible/roles/chef_deployment/tasks/deploy_chef_server.yml (complete) - Created deploy_chef_server.yml with tasks to set hostname, configure sysctl parameters, download and deploy Chef Infra Server only, and create Chef user and organization.

### Structure Files
- [x] N/A → ./ansible/roles/chef_deployment/meta/main.yml (complete) - Created meta/main.yml with role metadata including platforms, tags, and dependencies.
- [x] N/A → ./ansible/roles/chef_deployment/tasks/main.yml (complete) - Created main.yml task file that conditionally includes either deploy_automate.yml or deploy_chef_server.yml based on variables.
- [x] N/A → ./ansible/roles/chef_deployment/defaults/main.yml (complete) - Created defaults/main.yml with variables for Chef deployment including hostname, user details, organization details, and deployment type flags.
- [x] N/A → ./ansible/roles/chef_deployment/README.md (complete) - Created README.md with comprehensive documentation including role variables, examples, and deployment options.
- [x] N/A → ./ansible/roles/chef_deployment/handlers/main.yml (complete) - Created empty handlers/main.yml file as no handlers are needed for this role.
- [x] N/A → ./ansible/roles/chef_deployment/vars/main.yml (complete) - Created empty vars/main.yml file as no additional variables are needed for this role.
- [x] N/A → ansible/roles/chef_deployment/meta/main.yml (complete)

### Dependencies (requirements.yml)
- [x] N/A → ./ansible/roles/chef_deployment/requirements.yml (complete) - Created requirements.yml with ansible.posix collection dependency for sysctl module.


Telemetry:
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAPDiscoveryAgent: 14.99s
    Tokens: 22687 in, 570 out
    Tools: aap_list_collections: 1, aap_search_collections: 3
    collections_found: 0
  PlanningAgent: 37.61s
    Tokens: 70939 in, 2085 out
    Tools: add_checklist_task: 10, list_checklist_tasks: 2, list_directory: 1
  WriteAgent: 167.96s
    Tokens: 562121 in, 8203 out
    Tools: ansible_doc_lookup: 1, ansible_lint: 2, ansible_write: 13, get_checklist_summary: 1, list_checklist_tasks: 3, read_file: 2, update_checklist_task: 10, write_file: 3
    attempts: 1
    complete: True
    files_created: 11
    files_total: 11
  ValidationAgent: 9.36s
    collections_installed: 1
    collections_failed: 0
    validators_passed: ['ansible-lint', 'role-check']
    validators_failed: []
    attempts: 0
    complete: True
    has_errors: False