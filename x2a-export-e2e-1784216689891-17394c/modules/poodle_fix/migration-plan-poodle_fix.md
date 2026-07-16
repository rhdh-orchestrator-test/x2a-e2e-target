---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for FQCN module names, proper handler naming, and structural improvements to convert from a playbook to a proper role structure.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook file, not a proper Ansible role. The migration will create a proper role structure.**

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
defaults/main.yml (to be created)

**Meta:**
meta/main.yml (to be created)

**Templates:**
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration Fix** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Legacy pattern: Uses short-form module name `replace:`
   - Modern equivalent: Use FQCN `ansible.builtin.replace:`
   - Notifies handlers to restart services after configuration changes

2. **Service Restart Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch (defined as "Restart apache" but notified as "Restart apache2")
   - Modern equivalent: Ensure handler names match notification names exactly

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names with notifications | poodle_fix.yml | "Restart apache" vs "Restart apache2" |
| Playbook structure | Role structure | poodle_fix.yml | Convert standalone playbook to proper role |
| Missing `mode:` | Add `mode:` parameter | tasks/main.yml | File permissions best practice |
| Missing argument specs | Add argument specifications | meta/argument_specs.yml | Role validation |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None (uses only builtin modules)

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

For meta/argument_specs.yml:
- `apache_config_path`: 
  - type: str
  - default: "/etc/apache2/mods-available/ssl.conf"
  - description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: 
  - type: str
  - default: "-all +TLSv1.2"
  - description: "SSL protocol configuration string"
- `restart_apache`: 
  - type: bool
  - default: true
  - description: "Whether to restart Apache after configuration change"
- `restart_ssh`: 
  - type: bool
  - default: true
  - description: "Whether to restart SSH after configuration change"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- defaults/main.yml
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
    dest: "{{ apache_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol {{ ssl_protocol_setting }}'
    mode: '0644'
  notify:
    - Restart apache2
    - Restart sshd
  when: restart_apache | bool
```

### handlers/main.yml
```yaml
---
- name: Restart apache2
  ansible.builtin.service:
    name: apache2
    state: restarted
  when: restart_apache | bool

- name: Restart sshd
  ansible.builtin.service:
    name: sshd
    state: restarted
  when: restart_ssh | bool
```

### defaults/main.yml
```yaml
---
apache_config_path: "/etc/apache2/mods-available/ssl.conf"
ssl_protocol_setting: "-all +TLSv1.2"
restart_apache: true
restart_ssh: true
```

### meta/main.yml
```yaml
---
galaxy_info:
  author: Your Name
  description: Role to fix POODLE vulnerability in Apache SSL configuration
  company: Your Company
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