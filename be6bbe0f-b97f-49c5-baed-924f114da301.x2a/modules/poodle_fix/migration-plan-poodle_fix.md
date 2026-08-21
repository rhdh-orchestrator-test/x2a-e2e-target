---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This is a simple Ansible playbook that mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The playbook needs to be converted from a standalone playbook to a proper Ansible role structure with fully qualified collection names (FQCN) and modern syntax.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability by enforcing TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a role. We need to create a proper role structure.**

The original file:
```
chef-and-ansible/poodle_fix.yml
```

The new role structure will be:
```
tasks/main.yml
handlers/main.yml
meta/main.yml
README.md
```

**Task Files:**
- tasks/main.yml

**Handler Files:**
- handlers/main.yml

**Variable Files:**
- defaults/main.yml (to be created)

**Meta:**
- meta/main.yml (to be created)

**Templates:**
- None in original

**Static Files:**
- None in original

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart services
   - Modern equivalent: Use `ansible.builtin.replace` with proper documentation

2. **Service Restart** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Apache handler uses FQCN but SSH handler doesn't
   - Modern equivalent: Use FQCN for all handlers and ensure handler names match notification names

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `service:` | `ansible.builtin.service:` | poodle_fix.yml | FQCN for SSH handler |
| Handler name mismatch | Match handler names with notifications | poodle_fix.yml | "Restart apache2" notification vs "Restart apache" handler |
| Standalone playbook | Proper role structure | poodle_fix.yml | Convert to role with proper directory structure |
| Missing documentation | Add comments and documentation | All files | Document purpose, variables, and usage |
| Missing meta information | Add meta/main.yml | N/A | Add proper metadata |
| Missing variable definitions | Add defaults/main.yml | N/A | Make configuration customizable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: core

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates in the original playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'
- `ssl_protocol_setting`: string, default: '-all +TLSv1.2', description: 'SSL protocol settings for Apache'
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

# Check SSL/TLS configuration
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify SSH configuration
sshd -t

# Test SSL/TLS connection
openssl s_client -connect localhost:443 -tls1_2
```

## Implementation Details

### tasks/main.yml
```yaml
---
- name: Fix SSL in Apache to mitigate POODLE vulnerability
  ansible.builtin.replace:
    dest: "{{ apache_ssl_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "SSLProtocol {{ ssl_protocol_setting }}"
  notify:
    - Restart apache2
    - Restart sshd
  when: restart_apache | bool
  tags:
    - security
    - apache
    - ssl
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
apache_ssl_config_path: '/etc/apache2/mods-available/ssl.conf'
ssl_protocol_setting: '-all +TLSv1.2'
restart_apache: true
restart_ssh: true
```

### meta/main.yml
```yaml
---
galaxy_info:
  role_name: poodle_fix
  author: your_name
  description: Mitigates POODLE vulnerability in Apache by enforcing TLSv1.2
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
    - poodle

dependencies: []
```

### meta/argument_specs.yml
```yaml
---
argument_specs:
  main:
    short_description: Role to mitigate POODLE vulnerability in Apache
    description:
      - This role updates Apache SSL configuration to disable vulnerable SSL protocols
      - It enforces TLSv1.2 to mitigate the POODLE vulnerability
    options:
      apache_ssl_config_path:
        type: str
        default: '/etc/apache2/mods-available/ssl.conf'
        description: Path to Apache SSL configuration file
      ssl_protocol_setting:
        type: str
        default: '-all +TLSv1.2'
        description: SSL protocol settings for Apache
      restart_apache:
        type: bool
        default: true
        description: Whether to restart Apache after configuration changes
      restart_ssh:
        type: bool
        default: true
        description: Whether to restart SSH after configuration changes
```