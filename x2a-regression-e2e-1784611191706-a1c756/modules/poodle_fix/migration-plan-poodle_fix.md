---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper handler naming, and structured playbook organization.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate the POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a structured Ansible role.**

```
chef-and-ansible/poodle_fix.yml
```

The current implementation is a simple playbook file. For proper role structure, it should be reorganized into:

```
tasks/main.yml
handlers/main.yml
meta/main.yml
README.md
```

**Task Files:**
- tasks/main.yml (to be created)

**Handler Files:**
- handlers/main.yml (to be created)

**Variable Files:**
- defaults/main.yml (to be created)

**Meta:**
- meta/main.yml (to be created)

**Templates:**
None identified

**Static Files:**
None identified

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration Fix** (`poodle_fix.yml`):
   - Updates Apache SSL configuration to disable vulnerable protocols and enable only TLSv1.2
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart Apache and SSH services
   - Modern equivalent: Use `ansible.builtin.replace` with proper mode specification

2. **Service Handlers** (`poodle_fix.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Handler name mismatch: "Restart apache" vs "Restart apache2" in notification
   - Uses `ansible.builtin.service` module for service management
   - Modern equivalent: Ensure handler names match notification names exactly

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Missing `mode:` | Add `mode: '0644'` | poodle_fix.yml | File permissions |
| Handler name mismatch | Match handler name with notification | poodle_fix.yml | "Restart apache" vs "Restart apache2" |
| Standalone playbook | Structured role organization | poodle_fix.yml | Convert to proper role structure |
| Missing `changed_when` | Add idempotency controls | poodle_fix.yml | For better change tracking |
| Missing `backup: true` | Add backup option | poodle_fix.yml | For safer file modifications |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None identified
**External packages**: None directly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the current implementation.

## Argument Specification

For meta/argument_specs.yml:
- `ssl_protocols`: 
  - type: string
  - default: '-all +TLSv1.2'
  - description: 'SSL protocols to enable/disable in Apache configuration'
- `apache_config_path`:
  - type: string
  - default: '/etc/apache2/mods-available/ssl.conf'
  - description: 'Path to Apache SSL configuration file'
- `restart_services`:
  - type: list
  - default: ['apache2', 'sshd']
  - description: 'Services to restart after configuration changes'

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
```bash
# Verify Apache configuration syntax
apache2ctl configtest

# Check SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2

# Verify SSH configuration
sshd -t

# Test for POODLE vulnerability
nmap --script ssl-poodle -p 443 localhost
```

## Detailed Migration Steps

1. **Create proper role structure**:
   - Create directories: tasks, handlers, defaults, meta
   - Move tasks to tasks/main.yml
   - Move handlers to handlers/main.yml
   - Create defaults/main.yml with variables
   - Create meta/main.yml with role metadata

2. **Modernize tasks/main.yml**:
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: "{{ apache_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "SSLProtocol {{ ssl_protocols }}"
    mode: '0644'
    backup: true
  notify:
    - Restart apache2
    - Restart sshd
```

3. **Modernize handlers/main.yml**:
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

4. **Create defaults/main.yml**:
```yaml
---
ssl_protocols: "-all +TLSv1.2"
apache_config_path: "/etc/apache2/mods-available/ssl.conf"
restart_services:
  - apache2
  - sshd
```

5. **Create meta/main.yml**:
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

6. **Create meta/argument_specs.yml**:
```yaml
---
argument_specs:
  main:
    short_description: Role to fix POODLE vulnerability in Apache SSL configuration
    description:
      - Updates Apache SSL configuration to disable vulnerable protocols
      - Enables only TLSv1.2 to mitigate POODLE vulnerability
    options:
      ssl_protocols:
        type: str
        default: "-all +TLSv1.2"
        description: SSL protocols to enable/disable in Apache configuration
      apache_config_path:
        type: str
        default: "/etc/apache2/mods-available/ssl.conf"
        description: Path to Apache SSL configuration file
      restart_services:
        type: list
        default: 
          - apache2
          - sshd
        description: Services to restart after configuration changes
```