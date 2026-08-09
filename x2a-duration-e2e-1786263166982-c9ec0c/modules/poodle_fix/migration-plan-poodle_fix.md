---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper handler names, and structured playbook organization.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a structured Ansible role.**

poodle_fix.yml

## Module Explanation

The playbook performs operations in this order:

1. **poodle_fix.yml**:
   - Updates Apache SSL configuration to mitigate POODLE vulnerability by replacing the SSLProtocol line
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart Apache and SSH services
   - Handler name mismatch: notifies "Restart apache2" but handler is named "Restart apache"
   - Uses `become: yes` instead of `become: true`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean modernization |
| Handler name mismatch | Match handler names exactly | poodle_fix.yml | "Restart apache2" in notify vs "Restart apache" in handler |
| Standalone playbook | Convert to role structure | poodle_fix.yml | Create proper role directory structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are present in this playbook.

## Argument Specification

For a proper role conversion, the following variables should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: String, default: "/etc/apache2/mods-available/ssl.conf", path to Apache SSL configuration
- `ssl_protocol_setting`: String, default: "-all +TLSv1.2", SSL protocol settings to apply
- `restart_apache`: Boolean, default: true, whether to restart Apache after changes
- `restart_ssh`: Boolean, default: true, whether to restart SSH after changes

## Checks for the Migration

**Files to verify in the new role structure**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**: apache2, sshd

## Pre-flight checks:
```bash
# Verify Apache configuration syntax
apache2ctl configtest

# Verify SSH configuration syntax
sshd -t

# Check current SSL/TLS protocol settings
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify no SSLv3 (POODLE vulnerability) is enabled
openssl s_client -connect localhost:443 -ssl3
# Should fail with "ssl3 alert handshake failure" or similar
```

## Conversion to Role Structure

To convert this standalone playbook to a proper Ansible role, create the following structure:

**tasks/main.yml**:
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

**handlers/main.yml**:
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

**defaults/main.yml**:
```yaml
---
apache_ssl_config_path: /etc/apache2/mods-available/ssl.conf
ssl_protocol_setting: "-all +TLSv1.2"
restart_apache: true
restart_ssh: true
```

**meta/main.yml**:
```yaml
---
galaxy_info:
  author: Your Name
  description: Role to fix POODLE vulnerability in Apache
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

**meta/argument_specs.yml**:
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
        default: "-all +TLSv1.2"
        description: SSL protocol settings to apply
      restart_apache:
        type: bool
        default: true
        description: Whether to restart Apache after changes
      restart_ssh:
        type: bool
        default: true
        description: Whether to restart SSH after changes
```