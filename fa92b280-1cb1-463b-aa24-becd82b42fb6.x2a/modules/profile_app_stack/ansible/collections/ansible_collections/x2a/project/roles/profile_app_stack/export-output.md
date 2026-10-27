# MIGRATION FAILED for profile_app_stack

**Failure Reason:** Molecule generation/validation failed: Deployment playbook does not include x2a.project.profile_app_stack: ansible/run_profile_app_stack.yml

## Migration Summary

- **Total items:** 42
- **Completed:** 32
- **Pending:** 10
- **Missing:** 0
- **Errors:** 0
- **Write attempts:** 1
- **Validation attempts:** 0

## Partial Validation Report

_Not run_

### Review Report

## Review Summary

### Findings
- **[Missing package dependencies] Severity: High: `tasks/python.yml` - The role configured logrotate but did not install the `logrotate` package; health checks required `curl`; database backups required `sudo`. Fixed by adding these packages to the runtime package installation task.**
- **[Missing prerequisites] Severity: High: `tasks/main.yml` - `vars/common.yml` was never loaded, leaving database and application overrides undefined or incorrectly defaulted. Fixed by loading common variables before environment-specific variables.**
- **[Invalid variable reference] Severity: High: `tasks/app.yml` - The environment template used `profile_app_stack_app_app_port`, which is undefined. Fixed to use `profile_app_stack_app_port`.**
- **[Missing configured package installation] Severity: Medium: `tasks/app.yml` - `profile_app_stack_pip_packages` was defined but never installed. Fixed by adding an idempotent `ansible.builtin.pip` task.**
- **[Idempotency failure] Severity: Medium: `tasks/database.yml` - PostgreSQL role and database creation relied on parsing command failures and ran commands on every execution. Fixed by checking for existing roles/databases before creation.**
- **[Hardcoded runtime paths] Severity: Medium: `files/healthcheck.sh` - The script hardcoded the default application port and log directory, causing incorrect behavior when role variables were overridden. Fixed by converting it to `templates/healthcheck.sh.j2` and rendering configured values.**
- **[Application ownership prerequisite] Severity: Medium: `tasks/python.yml` - The role modified `/etc/logrotate.d/...` without ensuring logrotate existed. Fixed by installing the owning package before configuration.**
- **[Application ownership prerequisite] Severity: Medium: `tasks/monitoring.yml` - The role manages `prometheus-node-exporter`, and the package is now installed before the service is started in production. Already structurally ordered correctly after dependency fix.**

### Changes Made
- `tasks/main.yml`: Added loading of `vars/common.yml` before environment variables.
- `tasks/python.yml`: Added `curl`, `sudo`, and `logrotate` package dependencies.
- `tasks/database.yml`: Added idempotent PostgreSQL role/database existence checks.
- `tasks/app.yml`:
  - Added installation of configured `profile_app_stack_pip_packages`.
  - Corrected the application port variable reference.
  - Changed health-check deployment from `copy` to a variable-aware template.
- `templates/healthcheck.sh.j2`: Added configurable application port and log directory values.

### No Issues Found
- **Ordering:** Packages, users/groups, directories, application deployment, configuration, and service startup are now ordered correctly.
- **Invalid module parameters:** No unsupported module parameters were found.
- **Command idempotency:** Remaining command tasks are guarded by existence checks or appropriate conditional execution.
- **Handlers:** Referenced handlers exist and are valid.
- **Argument specifications:** `meta/argument_specs.yml` exists and covers the role defaults with matching types.

### Molecule Test Generation

**Status:** generation_failed_unverified

Static generation/validation failed: Deployment playbook does not include x2a.project.profile_app_stack: ansible/run_profile_app_stack.yml

### Partial Checklist

## Checklist: profile_app_stack

### Templates
- [x] site-modules/profile_app_stack/templates/logrotate.conf.erb → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/templates/logrotate.conf.j2 (complete)
- [x] site-modules/profile_app_stack/templates/app.env.erb → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/templates/app.env.j2 (complete)
- [x] site-modules/profile_app_stack/templates/app.service.epp → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/templates/app.service.j2 (complete)

### Recipes → Tasks
- [x] site-modules/profile_app_stack/manifests/init.pp → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/tasks/main.yml (complete)
- [x] site-modules/profile_app_stack/manifests/python.pp → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/tasks/python.yml (complete)
- [x] site-modules/profile_app_stack/manifests/database.pp → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/tasks/database.yml (complete)
- [x] site-modules/profile_app_stack/manifests/app.pp → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/tasks/app.yml (complete)
- [x] site-modules/profile_app_stack/manifests/service.pp → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/tasks/service.yml (complete)
- [x] site-modules/profile_app_stack/manifests/monitoring.pp → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/tasks/monitoring.yml (complete)
- [x] site-modules/profile/manifests/app/stack.pp → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/tasks/main.yml (complete)
- [x] site-modules/role/manifests/app_server.pp → ansible/run_profile_app_stack.yml (complete)

### Attributes → Variables
- [x] site-modules/profile_app_stack/hiera.yaml → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/vars/main.yml (complete)
- [x] site-modules/profile_app_stack/data/common.yaml → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/defaults/main.yml (complete)
- [x] site-modules/profile_app_stack/data/environment/production.yaml → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/vars/production.yml (complete)
- [x] site-modules/profile_app_stack/data/environment/staging.yaml → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/vars/staging.yml (complete)
- [x] data/common.yaml → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/vars/common.yml (complete)

### Static Files
- [x] puppet:///modules/profile_app_stack/backup.sh → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/files/backup.sh (complete)
- [x] puppet:///modules/profile_app_stack/healthcheck.sh → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/files/healthcheck.sh (complete)
- [x] site-modules/profile_app_stack/files/backup.sh → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/files/backup.sh (complete)
- [x] site-modules/profile_app_stack/files/healthcheck.sh → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/files/healthcheck.sh (complete)

### Structure Files
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/meta/main.yml (complete) - Created standard meta/main.yml
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/meta/argument_specs.yml (complete)
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/handlers/main.yml (complete)
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/defaults/main.yml (complete)
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/tasks/main.yml (complete)
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/requirements.yml (complete)
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/README.md (complete)
- [x] profile_app_stack::app_db_url → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/filter_plugins/app_db_url.py (complete)
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/vars/vault.yml (complete)

### Molecule Testing
- [ ] N/A → ansible/run_profile_app_stack.yml (pending)
- [ ] N/A → ansible/molecule/requirements.yml (pending)
- [ ] N/A → ansible/molecule/README.md (pending)
- [ ] N/A → ansible/molecule/profile_app_stack/molecule.yml (pending)
- [ ] N/A → ansible/molecule/profile_app_stack/inventory/hosts.yml (pending)
- [ ] N/A → ansible/molecule/profile_app_stack/create.yml (pending)
- [ ] N/A → ansible/molecule/profile_app_stack/destroy.yml (pending)
- [ ] N/A → ansible/molecule/profile_app_stack/prepare.yml (pending)
- [ ] N/A → ansible/molecule/profile_app_stack/converge.yml (pending)
- [ ] N/A → ansible/molecule/profile_app_stack/verify.yml (pending)

### Credentials → AAP Configuration
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/aap-configuration/controller_credential_types.yml (complete)
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/aap-configuration/controller_credentials.yml (complete)
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/profile_app_stack/tasks/validate_credentials.yml (complete)


## Telemetry

```
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAP Collection Discovery: 10.70s
    Tokens: 35329 in, 240 out
    Tools: aap_list_collections: 1, aap_search_collections: 6
    collections_found: 0
  Credential Extractor: 5.22s
    Tokens: 11343 in, 794 out
    credentials_found: 2
  Export Planner: 29.11s
    Tokens: 111799 in, 3628 out
    Tools: add_checklist_task: 29, get_checklist_summary: 1, list_checklist_tasks: 1, list_directory: 8
  Ansible Role Writer: 136.13s
    Tokens: 2214283 in, 10198 out
    Tools: ansible_doc_lookup: 1, ansible_lint: 1, ansible_write: 16, copy_file: 4, list_checklist_tasks: 3, list_directory: 2, read_file: 15, update_checklist_task: 28, write_file: 5
    attempts: 1
    complete: True
    files_created: 32
    files_total: 42
  ReviewAgent: 69.94s
    Tokens: 153621 in, 10718 out
    Tools: ansible_write: 6, list_directory: 2, read_file: 21, write_file: 1
  Molecule Test Generator: 0.05s
```