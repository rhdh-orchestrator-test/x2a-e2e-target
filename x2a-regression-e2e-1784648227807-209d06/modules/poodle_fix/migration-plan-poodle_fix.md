---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies security hardening for SSL/TLS by updating Apache's SSL configuration to disable vulnerable protocols and only allow TLSv1.2. The modernization needs include converting to FQCN module names, updating handler names to match notification names, and restructuring the playbook into a proper Ansible role format.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables all SSL protocols except TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a role. The migration will convert this to a proper role structure.**

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

1. **SSL Configuration** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable protocols
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart services
   - Modern equivalent: Use `ansible.builtin.replace` with proper indentation and formatting

2. **Service Restart Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Handler name mismatch: "Restart apache" vs "Restart apache2" in notification
   - Modern equivalent: Ensure handler names match notification names exactly

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names to notifications | poodle_fix.yml | "Restart apache" vs "Restart apache2" |
| Playbook format | Role structure | poodle_fix.yml | Convert standalone playbook to role |
| Missing `mode:` | Add `mode:` parameter | tasks/main.yml | File permissions best practice |
| Missing role metadata | Add `meta/main.yml` | N/A | Role metadata for Galaxy |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required for basic functionality

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the original playbook
- Consider adding:
  - `ssl_config_path`: Path to SSL config file (default: '/etc/apache2/mods-available/ssl.conf')
  - `ssl_protocol_string`: Protocol string to use (default: '-all +TLSv1.2')

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
```
# Verify Apache SSL configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Check Apache syntax
apache2ctl configtest

# Verify Apache is running with new settings
systemctl status apache2

# Verify SSH is running
systemctl status sshd
```

## Implementation Details

### tasks/main.yml
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: "{{ ssl_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "SSLProtocol {{ ssl_protocol_string }}"
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
ssl_config_path: /etc/apache2/mods-available/ssl.conf
ssl_protocol_string: "-all +TLSv1.2"
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
    - hardening

dependencies: []
```

### meta/argument_specs.yml
```yaml
---
argument_specs:
  main:
    short_description: Role to fix POODLE vulnerability in Apache SSL configuration
    description:
      - Updates Apache SSL configuration to mitigate POODLE vulnerability
      - Disables all SSL protocols except TLSv1.2
    options:
      ssl_config_path:
        description: Path to the Apache SSL configuration file
        type: str
        default: /etc/apache2/mods-available/ssl.conf
        required: false
      ssl_protocol_string:
        description: SSL protocol string to use in configuration
        type: str
        default: "-all +TLSv1.2"
        required: false
```