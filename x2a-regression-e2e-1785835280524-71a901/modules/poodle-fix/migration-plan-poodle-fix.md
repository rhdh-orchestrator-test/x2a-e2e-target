---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the file and create a migration plan based on the content:

# Migration Plan: poodle-fix

**TLDR**: This is a simple Ansible playbook that fixes SSL vulnerabilities in Apache by updating the SSL configuration to disable vulnerable protocols and enable only TLSv1.2. The playbook needs to be converted from a standalone playbook to a proper Ansible role structure with modernized syntax.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables all SSL protocols except TLSv1.2
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
- tasks/main.yml (to be created)

**Handler Files:**
- handlers/main.yml (to be created)

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

1. **SSL Configuration Update** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable protocols
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart services
   - Modern equivalent: Use `ansible.builtin.replace` with proper mode specification

2. **Service Restart Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Uses `ansible.builtin.service` module for Apache but without proper handler name matching
   - Uses `ansible.builtin.service` module for SSH
   - Modern equivalent: Ensure handler names match notification names

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Missing `mode` parameter | Add `mode: preserve` | poodle_fix.yml | File permissions |
| Handler name mismatch | Match handler name with notification | poodle_fix.yml | "Restart apache2" notification vs "Restart apache" handler |
| Missing `meta/main.yml` | Create proper role metadata | N/A | Role structure |
| Missing `defaults/main.yml` | Create variables for configuration | N/A | Parameterization |
| Hardcoded file paths | Use variables | poodle_fix.yml | Flexibility |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: '*'

**Role dependencies**: None identified
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the original playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'
- `ssl_protocol_setting`: string, default: '-all +TLSv1.2', description: 'SSL protocol configuration string'
- `restart_apache`: boolean, default: true, description: 'Whether to restart Apache after configuration changes'
- `restart_ssh`: boolean, default: true, description: 'Whether to restart SSH after configuration changes'

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

# Verify SSH configuration syntax
sshd -t

# Check SSL/TLS configuration
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify no SSLv3 (POODLE vulnerability)
openssl s_client -connect localhost:443 -ssl3
# Should fail with "ssl3 alert handshake failure"
```

## Implementation Details

### tasks/main.yml
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: "{{ apache_ssl_conf_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "SSLProtocol {{ ssl_protocol_setting }}"
    mode: preserve
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
apache_ssl_conf_path: /etc/apache2/mods-available/ssl.conf
ssl_protocol_setting: -all +TLSv1.2
restart_apache: true
restart_ssh: true
```

### meta/main.yml
```yaml
---
galaxy_info:
  role_name: poodle_fix
  author: your_name
  description: Role to fix POODLE vulnerability in Apache SSL configuration
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
      - This role updates Apache SSL configuration to mitigate POODLE vulnerability
      - Disables all SSL protocols except TLSv1.2
    options:
      apache_ssl_conf_path:
        type: str
        default: /etc/apache2/mods-available/ssl.conf
        description: Path to Apache SSL configuration file
      ssl_protocol_setting:
        type: str
        default: "-all +TLSv1.2"
        description: SSL protocol configuration string
      restart_apache:
        type: bool
        default: true
        description: Whether to restart Apache after configuration changes
      restart_ssh:
        type: bool
        default: true
        description: Whether to restart SSH after configuration changes
```