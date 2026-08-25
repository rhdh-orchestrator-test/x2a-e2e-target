---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and create a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This is a simple Ansible playbook that mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The playbook needs to be converted from a standalone playbook to a proper Ansible role structure with fully qualified collection names (FQCN) and modern syntax.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a role. We need to create a proper role structure.**

Current file:
```
chef-and-ansible/poodle_fix.yml
```

Proposed role structure:
```
tasks/main.yml
handlers/main.yml
meta/main.yml
README.md
```

**Task Files:**
tasks/main.yml

**Handler Files:**
handlers/main.yml

**Variable Files:**
defaults/main.yml

**Meta:**
meta/main.yml

**Templates:**
None identified

**Static Files:**
None identified

## Module Explanation

The role performs operations in this order:

1. **Security Hardening** (`tasks/main.yml`):
   - Updates Apache SSL configuration to mitigate POODLE vulnerability
   - Uses the `replace` module to modify SSL configuration
   - Legacy pattern: short module name `replace:` without FQCN
   - Modern equivalent: `ansible.builtin.replace:`
   - Ansible module mapping: `replace:` → `ansible.builtin.replace:`

2. **Service Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - One handler already uses FQCN (`ansible.builtin.service:`)
   - Handler name mismatch: Defined as "Restart apache" but notified as "Restart apache2"

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Handler name mismatch | Match handler names exactly | handlers/main.yml | "Restart apache" vs "Restart apache2" |
| Standalone playbook | Proper role structure | All files | Convert to role structure |
| Missing `mode:` parameter | Add `mode:` parameter | tasks/main.yml | For file operations |
| Missing `changed_when` | Add `changed_when` condition | tasks/main.yml | For idempotency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the current playbook.

## Argument Specification

For meta/argument_specs.yml:
- `ssl_protocol`: string, default: '-all +TLSv1.2', description: "SSL protocols to enable/disable"
- `apache_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: "Path to Apache SSL configuration file"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- defaults/main.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache configuration syntax
apache2ctl configtest

# Check SSL/TLS configuration
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify SSH configuration
sshd -t

# Test for POODLE vulnerability
openssl s_client -connect localhost:443 -ssl3
# Should fail with "wrong version number" if properly mitigated
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
```

### meta/main.yml
```yaml
---
galaxy_info:
  role_name: poodle_fix
  author: your_name
  description: Mitigates POODLE vulnerability in Apache SSL configuration
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
    short_description: Mitigates POODLE vulnerability in Apache SSL configuration
    description:
      - This role updates Apache SSL configuration to disable vulnerable SSL protocols
      - Enables only TLSv1.2 to mitigate POODLE vulnerability
    options:
      ssl_protocol:
        type: str
        default: "-all +TLSv1.2"
        description: SSL protocols to enable/disable
      apache_config_path:
        type: str
        default: "/etc/apache2/mods-available/ssl.conf"
        description: Path to Apache SSL configuration file
```