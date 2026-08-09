---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for FQCN module names, handler naming consistency, and proper file structure to convert from a playbook to a proper Ansible role.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The current implementation is a standalone playbook, not a proper role structure. The migration will create a proper role structure.**

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
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **Main Tasks** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Legacy pattern: Short module name `replace:` without FQCN
   - Modern equivalent: `ansible.builtin.replace:`
   - Ansible module mapping: `replace:` → `ansible.builtin.replace:`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name inconsistency | Consistent handler names | poodle_fix.yml | Handler name in notify ("Restart apache2") doesn't match handler name ("Restart apache") |
| Playbook structure | Role structure | poodle_fix.yml | Convert from playbook to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required, only uses built-in modules

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables are defined in the current implementation, but could add:
  - `ssl_protocol`: string, default: '-all +TLSv1.2', description: 'SSL protocols to enable/disable'
  - `apache_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'

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
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Check Apache SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Validate Apache configuration: `apache2ctl configtest`

## Migration Implementation Details

### tasks/main.yml
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: /etc/apache2/mods-available/ssl.conf
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol {{ ssl_protocol }}'
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
```