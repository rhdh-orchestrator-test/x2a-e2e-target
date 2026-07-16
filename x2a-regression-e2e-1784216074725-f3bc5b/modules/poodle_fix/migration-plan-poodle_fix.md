---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for syntax updates, including fully qualified collection names (FQCN) for modules and proper handler naming.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 for secure communications
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Updates the Apache SSL configuration file to mitigate the POODLE vulnerability
   - Replaces the SSLProtocol directive to only allow TLSv1.2 and disable all other protocols
   - Notifies handlers to restart Apache and SSH services
   - Legacy pattern: Uses short module name `replace` instead of FQCN
   - Modern equivalent: Use `ansible.builtin.replace` with proper parameter formatting

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler name in notify and handler definition | poodle_fix.yml | Handler "Restart apache2" in notify doesn't match "Restart apache" in handler definition |
| Playbook structure | Convert to proper role structure | poodle_fix.yml | Convert from standalone playbook to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are present in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables are defined in the current playbook, but the following could be added for flexibility:
  - `apache_ssl_config_path`: String, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'
  - `ssl_protocol_setting`: String, default: '-all +TLSv1.2', description: 'SSL protocol settings for Apache'

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
- Verify Apache configuration syntax: `apache2ctl configtest`
- Check SSL/TLS configuration: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify SSH configuration: `sshd -t`
- Test SSL/TLS connection: `openssl s_client -connect localhost:443 -tls1_2`

## Migration Steps

1. **Create proper role structure**:
   - Create directory structure: `mkdir -p tasks handlers defaults meta`
   - Move task to tasks/main.yml
   - Move handlers to handlers/main.yml
   - Create meta/main.yml with role metadata
   - Create defaults/main.yml with default variables

2. **tasks/main.yml**:
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: "{{ apache_ssl_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "SSLProtocol {{ ssl_protocol_setting }}"
  notify:
    - Restart apache2
    - Restart sshd
```

3. **handlers/main.yml**:
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

4. **defaults/main.yml**:
```yaml
---
apache_ssl_config_path: /etc/apache2/mods-available/ssl.conf
ssl_protocol_setting: -all +TLSv1.2
```

5. **meta/main.yml**:
```yaml
---
galaxy_info:
  author: Your Name
  description: Role to fix POODLE vulnerability in Apache
  company: Your Company
  license: license (MIT, BSD)
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

6. **meta/argument_specs.yml**:
```yaml
---
argument_specs:
  main:
    short_description: Role to fix POODLE vulnerability in Apache
    description:
      - This role updates Apache SSL configuration to mitigate the POODLE vulnerability
      - It disables vulnerable SSL protocols and enables only TLSv1.2
    options:
      apache_ssl_config_path:
        type: str
        default: /etc/apache2/mods-available/ssl.conf
        description: Path to Apache SSL configuration file
      ssl_protocol_setting:
        type: str
        default: -all +TLSv1.2
        description: SSL protocol settings for Apache
```