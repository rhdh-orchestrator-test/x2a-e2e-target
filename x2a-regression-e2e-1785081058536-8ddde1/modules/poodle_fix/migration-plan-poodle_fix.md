---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The modernization needs include converting to FQCN module names, fixing handler names, and restructuring the playbook into a proper Ansible role format.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a role. The migration will convert this to a proper role structure.**

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
tasks/main.yml (to be created)

**Handler Files:**
handlers/main.yml (to be created)

**Variable Files:**
defaults/main.yml (to be created if needed)

**Meta:**
meta/main.yml (to be created)

**Templates:**
None identified

**Static Files:**
None identified

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration Update** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable protocols and enable only TLSv1.2
   - Legacy pattern: Uses short module name `replace` without FQCN
   - Modern equivalent: Use `ansible.builtin.replace` with proper FQCN
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Restart Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch (defined as "Restart apache" but notified as "Restart apache2")
   - Modern equivalent: Ensure handler names match notification names exactly
   - Ansible module mapping: Already using FQCN `ansible.builtin.service`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names with notifications | poodle_fix.yml | "Restart apache" vs "Restart apache2" |
| Standalone playbook | Proper role structure | poodle_fix.yml | Convert to role with tasks/main.yml and handlers/main.yml |
| No argument specs | Add meta/argument_specs.yml | N/A | Define role parameters |
| No role metadata | Add meta/main.yml | N/A | Define role metadata |

## Dependencies

**Collection dependencies** (for requirements.yml):
- No external collections required, only ansible.builtin modules are used

**Role dependencies**: None identified
**External packages**: None directly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the current playbook.

## Argument Specification

Proposed variables for meta/argument_specs.yml:
- `apache_ssl_config_path`: 
  - Type: string
  - Default: "/etc/apache2/mods-available/ssl.conf"
  - Description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: 
  - Type: string
  - Default: "-all +TLSv1.2"
  - Description: "SSL protocol settings to mitigate POODLE vulnerability"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- meta/argument_specs.yml
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
# Should fail with "wrong version number" if properly configured
```

## Implementation Details

### tasks/main.yml
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: "{{ apache_ssl_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol {{ ssl_protocol_setting }}'
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
apache_ssl_config_path: /etc/apache2/mods-available/ssl.conf
ssl_protocol_setting: "-all +TLSv1.2"
```

### meta/main.yml
```yaml
---
galaxy_info:
  role_name: poodle_fix
  author: your_name
  description: Mitigates POODLE vulnerability in Apache and SSH
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