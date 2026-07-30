---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This is a simple Ansible playbook that mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The playbook needs to be converted from a standalone playbook to a proper Ansible role structure with modernized syntax.

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

1. **Main Tasks** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart services
   - Modern equivalent: Use `ansible.builtin.replace` with proper mode specification

2. **Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Uses `ansible.builtin.service` module for Apache but without proper handler name matching
   - Uses `ansible.builtin.service` module for SSH
   - Modern equivalent: Ensure handler names match notification names

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Missing `mode:` | Add `mode: preserve` | poodle_fix.yml | File permissions |
| Handler name mismatch | Match handler name with notification | poodle_fix.yml | "Restart apache2" notification vs "Restart apache" handler |
| Playbook structure | Role structure | poodle_fix.yml | Convert standalone playbook to role |
| Missing `changed_when` | Add appropriate change detection | poodle_fix.yml | Idempotency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin

**Role dependencies**: None identified
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the current playbook.

## Argument Specification

For meta/argument_specs.yml:
- `apache_ssl_config_path`: 
  - type: str
  - default: "/etc/apache2/mods-available/ssl.conf"
  - description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: 
  - type: str
  - default: "-all +TLSv1.2"
  - description: "SSL protocol settings to mitigate POODLE vulnerability"

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
# Verify Apache configuration syntax
apache2ctl configtest

# Check SSL/TLS protocols enabled
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify SSH configuration
sshd -t

# Check services are running
systemctl status apache2
systemctl status sshd
```

## Detailed Migration Steps

### 1. Create Role Directory Structure
```
mkdir -p poodle_fix/{tasks,handlers,defaults,meta}
```

### 2. Create tasks/main.yml
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: "{{ apache_ssl_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol {{ ssl_protocol_setting }}'
    mode: preserve
  notify:
    - Restart apache2
    - Restart sshd
  register: ssl_config_update
  changed_when: ssl_config_update.changed
```

### 3. Create handlers/main.yml
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

### 4. Create defaults/main.yml
```yaml
---
apache_ssl_config_path: /etc/apache2/mods-available/ssl.conf
ssl_protocol_setting: "-all +TLSv1.2"
```

### 5. Create meta/main.yml
```yaml
---
galaxy_info:
  author: Your Name
  description: Role to mitigate POODLE vulnerability in Apache
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

### 6. Create meta/argument_specs.yml
```yaml
---
argument_specs:
  main:
    short_description: Role to mitigate POODLE vulnerability in Apache
    description:
      - This role updates Apache SSL configuration to disable vulnerable SSL protocols
      - Enables only TLSv1.2 to mitigate the POODLE vulnerability
    options:
      apache_ssl_config_path:
        type: str
        default: /etc/apache2/mods-available/ssl.conf
        description: Path to Apache SSL configuration file
      ssl_protocol_setting:
        type: str
        default: "-all +TLSv1.2"
        description: SSL protocol settings to mitigate POODLE vulnerability
```