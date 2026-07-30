---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and handler name consistency.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a playbook, not a role structure. For migration to a proper role structure, we need to create the following files:**

```
tasks/main.yml
handlers/main.yml
meta/main.yml
README.md
```

**Task Files:**
- tasks/main.yml (to be created from playbook tasks)

**Handler Files:**
- handlers/main.yml (to be created from playbook handlers)

**Variable Files:**
- defaults/main.yml (to be created)

**Meta:**
- meta/main.yml (to be created)

**Templates:**
- None identified in the original playbook

**Static Files:**
- None identified in the original playbook

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration** (`tasks/main.yml`):
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart services after configuration changes
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Restart Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Uses `ansible.builtin.service` module for Apache but lacks FQCN consistency
   - Ansible module mapping: `service` → `ansible.builtin.service` (for consistency)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Handler name inconsistency (`Restart apache2` vs `Restart apache`) | Consistent handler naming | handlers/main.yml, tasks/main.yml | Handler name in notify should match handler name |
| Playbook structure | Role structure | All files | Convert from playbook to proper role structure |
| Missing `mode` parameter | Add `mode` parameter for file operations | tasks/main.yml | Ensure idempotency and security |
| Missing role metadata | Create proper meta/main.yml | meta/main.yml | Add role metadata |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: core

**Role dependencies**: None identified
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the original playbook.

## Argument Specification

For meta/argument_specs.yml:
- `ssl_protocol`: string, default: '-all +TLSv1.2', description: "SSL protocols to enable/disable"
- `apache_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: "Path to Apache SSL configuration file"
- `restart_services`: boolean, default: true, description: "Whether to restart services after configuration changes"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
```
# Verify Apache configuration syntax
apache2ctl configtest

# Check SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2

# Verify SSH configuration
sshd -t

# Test for POODLE vulnerability
nmap --script ssl-enum-ciphers -p 443 localhost
```

## Implementation Details

### tasks/main.yml
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: "{{ apache_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "SSLProtocol {{ ssl_protocol }}"
    mode: '0644'
  notify:
    - Restart apache
    - Restart sshd
```

### handlers/main.yml
```yaml
---
- name: Restart apache
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
restart_services: true
```

### meta/main.yml
```yaml
---
galaxy_info:
  role_name: poodle_fix
  author: your_name
  description: Fixes POODLE vulnerability in Apache SSL configuration
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

### meta/argument_specs.yml
```yaml
---
argument_specs:
  main:
    short_description: Role to fix POODLE vulnerability in Apache SSL configuration
    description:
      - This role updates Apache SSL configuration to disable vulnerable SSL protocols
      - and enable only TLSv1.2 to mitigate the POODLE vulnerability
    options:
      ssl_protocol:
        type: str
        default: "-all +TLSv1.2"
        description: SSL protocols to enable/disable
      apache_config_path:
        type: str
        default: "/etc/apache2/mods-available/ssl.conf"
        description: Path to Apache SSL configuration file
      restart_services:
        type: bool
        default: true
        description: Whether to restart services after configuration changes
```