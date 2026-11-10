# MIGRATION FAILED for nginx_multisite

**Failure Reason:** Molecule generation/validation failed: verify.yml assertions must check concrete expected behavior

## Migration Summary

- **Total items:** 24
- **Completed:** 14
- **Pending:** 9
- **Missing:** 0
- **Errors:** 1
- **Write attempts:** 1
- **Validation attempts:** 0

## Partial Validation Report

_Not run_

### Review Report

## Review Summary

### Findings
- **[Missing package dependency] Severity: High: `tasks/security.yml` - SSH configuration tasks and `sshd` handler depended on an SSH server package that the role did not install.** Fixed by adding `openssh-server` to the security package list and using the platform-specific service name (`ssh` on Debian, `sshd` on RedHat).
- **[Missing prerequisite] Severity: High: `tasks/nginx.yml` - Site document roots and index files used the hard-coded `nginx` user/group, which does not exist by default on Debian-based systems where nginx runs as `www-data`.** Fixed by using `nginx_multisite_nginx_user` for ownership and selecting the platform-appropriate default user.
- **[Missing source files] Severity: High: `tasks/nginx.yml` - `copy` tasks referenced site index files that were absent from the role.** Fixed by adding index files for all three default sites:
  - `files/test.cluster.local/index.html`
  - `files/ci.cluster.local/index.html`
  - `files/status.cluster.local/index.html`
- **[Missing application guard] Severity: Medium: `tasks/security.yml` - SSH configuration edits could create or modify `/etc/ssh/sshd_config` on systems without an SSH daemon.** Fixed by installing `openssh-server`, checking the file with `stat`, and setting `create: false` on both `lineinfile` tasks.
- **[Idempotency] Severity: Low: `tasks/ssl.yml` - Certificate generation was guarded with `creates`, preventing repeated certificate generation.** No additional change required.
- **[Invalid module parameters] Severity: None - No invalid Ansible module parameters were found.**
- **[Missing argument specifications] Severity: None - `meta/argument_specs.yml` exists and covers the defaults.**
- **[Ordering] Severity: None - Required packages are installed before their configuration and service tasks.**

### Changes Made
- `tasks/security.yml`
  - Added `openssh-server` installation.
  - Added SSH configuration existence check.
  - Added `create: false` and existence conditions to SSH hardening tasks.
- `tasks/nginx.yml`
  - Changed site root and index ownership to `nginx_multisite_nginx_user`.
- `defaults/main.yml`
  - Selected `www-data` on Debian-family systems and `nginx` elsewhere.
- `handlers/main.yml`
  - Selected `ssh` or `sshd` based on the target OS family.
- Added missing site content files:
  - `files/test.cluster.local/index.html`
  - `files/ci.cluster.local/index.html`
  - `files/status.cluster.local/index.html`

### No Issues Found
- No invalid module parameters.
- No missing argument specification file.
- No unguarded clone/user-add/unarchive-style commands.
- No service-start-before-package-install ordering defects.
- SSL certificate generation already had an idempotency guard.

### Molecule Test Generation

**Status:** generation_failed_unverified

Static generation/validation failed: verify.yml assertions must check concrete expected behavior

### Partial Checklist

## Checklist: nginx_multisite

### Templates
- [x] cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/templates/fail2ban.jail.local.j2 (complete)
- [x] cookbooks/nginx-multisite/templates/default/nginx.conf.erb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/templates/nginx.conf.j2 (complete)
- [x] cookbooks/nginx-multisite/templates/default/security.conf.erb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/templates/security.conf.j2 (complete)
- [x] cookbooks/nginx-multisite/templates/default/site.conf.erb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/templates/site.conf.j2 (complete)
- [x] cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/templates/sysctl-security.conf.j2 (complete)

### Recipes → Tasks
- [x] cookbooks/nginx-multisite/recipes/default.rb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/tasks/main.yml (complete)
- [x] cookbooks/nginx-multisite/recipes/security.rb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/tasks/security.yml (complete)
- [x] cookbooks/nginx-multisite/recipes/nginx.rb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/tasks/nginx.yml (complete)
- [x] cookbooks/nginx-multisite/recipes/ssl.rb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/tasks/ssl.yml (complete)
- [x] cookbooks/nginx-multisite/recipes/sites.rb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/tasks/sites.yml (complete)

### Attributes → Variables
- [x] cookbooks/nginx-multisite/attributes/default.rb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/defaults/main.yml (complete)

### Structure Files
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/meta/main.yml (complete) - Created standard meta/main.yml
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/handlers/main.yml (complete)
- [x] ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/defaults/main.yml → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/meta/argument_specs.yml (complete)

### Molecule Testing
- [ ] N/A → ansible/run_nginx_multisite.yml (pending)
- [ ] N/A → ansible/molecule/requirements.yml (pending)
- [ ] N/A → ansible/molecule/README.md (pending)
- [ ] N/A → ansible/molecule/nginx_multisite/molecule.yml (pending)
- [ ] N/A → ansible/molecule/nginx_multisite/inventory/hosts.yml (pending)
- [ ] N/A → ansible/molecule/nginx_multisite/create.yml (pending)
- [ ] N/A → ansible/molecule/nginx_multisite/destroy.yml (pending)
- [ ] N/A → ansible/molecule/nginx_multisite/prepare.yml (pending)
- [ ] N/A → ansible/molecule/nginx_multisite/converge.yml (pending)
- [!] N/A → ansible/molecule/nginx_multisite/verify.yml (error) - verify.yml assertions must check concrete expected behavior


## Telemetry

```
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAP Collection Discovery: 20.19s
    Tokens: 29160 in, 377 out
    Tools: aap_search_collections: 10
    collections_found: 0
  Credential Extractor: 1.59s
    Tokens: 9418 in, 55 out
  Export Planner: 16.50s
    Tokens: 37858 in, 2171 out
    Tools: add_checklist_task: 14, list_checklist_tasks: 1, list_directory: 3
  Ansible Role Writer: 116.28s
    Tokens: 808515 in, 9083 out
    Tools: ansible_doc_lookup: 1, ansible_lint: 1, ansible_write: 10, file_search: 1, list_checklist_tasks: 2, list_directory: 3, read_file: 2, update_checklist_task: 13, write_file: 5
    attempts: 1
    complete: True
    files_created: 14
    files_total: 24
  ReviewAgent: 52.78s
    Tokens: 109146 in, 8583 out
    Tools: ansible_write: 5, list_directory: 6, read_file: 17, write_file: 3
  Molecule Test Generator: 104.45s
    Tokens: 139029 in, 17350 out
    Tools: ansible_lint: 3, ansible_role_check: 3, write_file: 4
```