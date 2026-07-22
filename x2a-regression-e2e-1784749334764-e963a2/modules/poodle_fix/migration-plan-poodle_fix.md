---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and provide a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This is a simple Ansible playbook (not a role) that mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The playbook needs to be converted to a proper role structure with modernized syntax including fully qualified collection names (FQCN) and proper handler naming.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a role. We need to create a proper role structure.**

For the new role structure:
```
tasks/main.yml
handlers/main.yml
meta/main.yml
README.md
```

**Task Files:**
tasks/main.yml (to be created)

**Handler Files:**
handlers/main.yml (to be created)

**Variable Files:**
defaults/main.yml (to be created)

**Meta:**
meta/main.yml (to be created)

**Templates:**
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **main.yml** (`tasks/main.yml`):
   - Updates Apache SSL configuration to mitigate POODLE vulnerability
   - Legacy pattern: Uses short-form module name `replace:` without FQCN
   - Modern equivalent: Use `ansible.builtin.replace:`
   - Ansible module mapping: `replace:` → `ansible.builtin.replace:`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | Handler name in notify ("Restart apache2") doesn't match handler name ("Restart apache") |
| Missing `mode:` parameter | Add `mode:` parameter | tasks/main.yml | File permissions should be explicitly set for security |
| Missing `backup:` parameter | Add `backup: true` | tasks/main.yml | Best practice to create backup before modifying config files |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: '*'

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

For meta/argument_specs.yml:
- `ssl_protocol`: string, default: '-all +TLSv1.2', description: "SSL protocols to enable/disable"
- `apache_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: "Path to Apache SSL configuration file"
- `restart_services`: list, default: ['apache2', 'sshd'], description: "Services to restart after configuration change"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- defaults/main.yml
- README.md

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache configuration syntax
apache2ctl configtest

# Verify SSH configuration syntax
sshd -t

# Check SSL/TLS configuration
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify no SSLv3 (POODLE vulnerability) is enabled
openssl s_client -connect localhost:443 -ssl3
# Should fail with "ssl3 alert handshake failure" or similar
```

## Implementation Details

### tasks/main.yml
```yaml
---
- name: Fix SSL in Apache to mitigate POODLE vulnerability
  ansible.builtin.replace:
    path: "{{ apache_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "SSLProtocol {{ ssl_protocol }}"
    backup: true
    mode: preserve
  notify:
    - Restart apache2
    - Restart sshd
```

### handlers/main.yml
```yaml
---
- name: Restart apache2
  ansible.builtin.service:
    name: apache2
    state: restarted

- name: Restart sshd
  ansible.builtin.service:
    name: sshd
    state: restarted
```

### defaults/main.yml
```yaml
---
ssl_protocol: "-all +TLSv1.2"
apache_config_path: "/etc/apache2/mods-available/ssl.conf"
restart_services:
  - apache2
  - sshd
```

### meta/main.yml
```yaml
---
galaxy_info:
  role_name: poodle_fix
  author: your_name
  description: Role to mitigate POODLE vulnerability in Apache
  license: MIT
  min_ansible_version: 2.9
  platforms:
    - name: Debian
      versions:
        - all
    - name: Ubuntu
      versions:
        - all
  galaxy_tags:
    - security
    - apache
    - ssl
    - poodle

dependencies: []
```