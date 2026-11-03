# MIGRATION FAILED for nginx_multisite

**Failure Reason:** Molecule generation/validation failed: verify.yml assertions must check concrete expected behavior

## Migration Summary

- **Total items:** 24
- **Completed:** 14
- **Pending:** 9
- **Missing:** 0
- **Errors:** 1
- **Write attempts:** 2
- **Validation attempts:** 0

## Partial Validation Report

_Not run_

### Review Report

## Review Summary

### Findings
- [Missing prerequisites] High: `tasks/main.yml` / `defaults/main.yml` - Tasks referenced `nginx_multisite_sites`, but the variable was not defined in defaults. Added an empty default mapping and argument specification.
- [Missing prerequisites] High: `tasks/nginx.yml` and `tasks/sites.yml` - Nginx configuration directories (`conf.d`, `sites-available`, and `sites-enabled`) were assumed to exist. Added explicit directory creation after nginx installation.
- [Missing prerequisites] Medium: `tasks/security.yml` - `/etc/sysctl.d` was assumed to exist. Added a directory creation task.
- [Missing package dependency] High: `tasks/security.yml` - SSH configuration and service management were present without ensuring an SSH server package existed. Added `openssh-server`.
- [Missing application/package dependency] High: `handlers/main.yml` - Handlers were empty even though tasks notified `Restart fail2ban`, `Restart ssh`, and `Reload nginx`. Added all handlers.
- [Missing application/package dependency] Medium: `tasks/security.yml` - SSH configuration changes could create a bogus configuration on systems without SSH. Added `stat`, `when`, and `create: false`.
- [Idempotency] Low: UFW configuration used raw commands with `changed_when: false`, masking actual changes. Replaced them with idempotent `community.general.ufw` tasks.
- [Missing argument specs] Medium: `meta/argument_specs.yml` did not describe the `nginx_multisite_sites` variable actually used by the role. Added the variable with a dictionary type and default.
- [Ordering] Medium: fail2ban configuration was deployed after starting the service, allowing the service to start with the wrong configuration. Moved configuration deployment before service startup.

### Changes Made
- `defaults/main.yml`: Added `nginx_multisite_sites: {}` and documentation.
- `meta/argument_specs.yml`: Added argument specification for `nginx_multisite_sites` and updated the role description.
- `handlers/main.yml`: Added fail2ban restart, SSH restart, and nginx reload handlers.
- `tasks/security.yml`:
  - Added `openssh-server` installation.
  - Moved fail2ban configuration before service startup.
  - Replaced non-idempotent UFW commands with `community.general.ufw`.
  - Added `/etc/sysctl.d` creation.
  - Guarded SSH configuration edits with `stat` and `create: false`.
- `tasks/nginx.yml`: Added creation of nginx configuration directories before deploying files.
- `tasks/sites.yml`: Added an explicit mode to the site symlink task and retained safe quoted paths.
- `handlers/main.yml`: Made the SSH service name platform-aware (`ssh` on Debian-family systems and `sshd` on RedHat-family systems).

### No Issues Found
- Invalid module parameters: No remaining invalid parameters found.
- Command idempotency: Certificate generation already used `creates:`.
- TLS prerequisites: OpenSSL, certificate directories, private-key directory, and `ssl-cert` group are created before certificate operations.
- Service ordering: Nginx is installed before configuration and started only after configuration deployment.
- File ownership prerequisites: `www-data` is provided by the nginx package, and `ssl-cert` is explicitly created.

### Molecule Test Generation

**Status:** generation_failed_unverified

Static generation/validation failed: verify.yml assertions must check concrete expected behavior

### Partial Checklist

## Checklist: nginx_multisite

### Templates
- [x] cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/templates/fail2ban.jail.local.j2 (complete) - Reconstructed static fail2ban jail configuration from migration plan because source ERB was absent.
- [x] cookbooks/nginx-multisite/templates/default/nginx.conf.erb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/templates/nginx.conf.j2 (complete) - Reconstructed nginx base configuration from migration plan because source ERB was absent.
- [x] cookbooks/nginx-multisite/templates/default/security.conf.erb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/templates/security.conf.j2 (complete) - Reconstructed nginx security configuration from migration plan because source ERB was absent.
- [x] cookbooks/nginx-multisite/templates/default/site.conf.erb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/templates/site.conf.j2 (complete) - Reconstructed parameterized virtual host template from migration plan because source ERB was absent.
- [x] cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/templates/sysctl-security.conf.j2 (complete) - Reconstructed static sysctl hardening configuration from migration plan because source ERB was absent.

### Recipes → Tasks
- [x] cookbooks/nginx-multisite/recipes/default.rb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/tasks/main.yml (complete) - Preserved Chef recipe include order with Ansible task includes.
- [x] cookbooks/nginx-multisite/recipes/security.rb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/tasks/security.yml (complete) - Converted package, fail2ban, UFW, sysctl, and SSH hardening operations using builtin modules and ansible.posix.sysctl.
- [x] cookbooks/nginx-multisite/recipes/nginx.rb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/tasks/nginx.yml (complete) - Converted nginx installation, configuration, service, document roots, and static content deployment.
- [x] cookbooks/nginx-multisite/recipes/ssl.rb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/tasks/ssl.yml (complete) - Converted TLS package/group/directory setup and idempotent openssl certificate generation with key permissions.
- [x] cookbooks/nginx-multisite/recipes/sites.rb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/tasks/sites.yml (complete) - Converted virtual host template deployment, enabled-site symlinks, default-site removal, and reload notifications.

### Structure Files
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/meta/main.yml (complete) - Created standard meta/main.yml
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/handlers/main.yml (complete) - Created handlers for fail2ban, SSH, and nginx lifecycle notifications.
- [x] cookbooks/nginx-multisite/attributes/default.rb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/defaults/main.yml (complete) - Source attributes file absent; site definitions reconstructed from migration plan.
- [x] cookbooks/nginx-multisite/attributes/default.rb → ansible/collections/ansible_collections/x2a/project/roles/nginx_multisite/meta/argument_specs.yml (complete) - Generated argument specifications from migrated nginx_multisite_sites defaults.

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
  AAP Collection Discovery: 14.93s
    Tokens: 27492 in, 324 out
    Tools: aap_list_collections: 1, aap_search_collections: 5
    collections_found: 0
  Credential Extractor: 1.93s
    Tokens: 8898 in, 74 out
  Export Planner: 12.15s
    Tokens: 26351 in, 1705 out
    Tools: add_checklist_task: 14, list_checklist_tasks: 1
  Ansible Role Writer: 194.85s
    Tokens: 1546826 in, 16278 out
    Tools: ansible_doc_lookup: 3, ansible_lint: 1, ansible_write: 14, list_checklist_tasks: 4, list_directory: 4, read_file: 4, update_checklist_task: 27, write_file: 13
    attempts: 2
    complete: True
    files_created: 14
    files_total: 24
  ReviewAgent: 64.04s
    Tokens: 129740 in, 9048 out
    Tools: ansible_write: 8, file_search: 3, list_directory: 4, read_file: 20
  Molecule Test Generator: 97.45s
    Tokens: 133903 in, 12303 out
    Tools: ansible_lint: 4, ansible_role_check: 4, write_file: 4
```