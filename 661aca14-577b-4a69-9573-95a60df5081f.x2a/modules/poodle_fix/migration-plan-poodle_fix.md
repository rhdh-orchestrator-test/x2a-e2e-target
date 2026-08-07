---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper handler naming, and structured playbook organization following current Ansible best practices.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Updates Apache SSL configuration to mitigate the POODLE vulnerability by replacing the SSLProtocol line to only allow TLSv1.2
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart Apache and SSH services
   - Contains handlers directly in the playbook rather than in a separate handlers file
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | Handler name "Restart apache" doesn't match notification "Restart apache2" |
| Playbook structure | Role structure | poodle_fix.yml | Convert from single playbook to proper role structure |
| Missing mode parameter | Add `mode:` parameter | poodle_fix.yml | File operations should specify mode for idempotency |
| Missing `changed_when` | Add `changed_when` condition | poodle_fix.yml | For better idempotency tracking |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None
**Services managed**: apache2, sshd

## Template Modernization

No templates present in the current implementation.

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
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Check SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Validate Apache configuration: `apache2ctl configtest`
- Test SSL connection: `openssl s_client -connect localhost:443 -tls1_2`
- Verify no SSLv3 support: `openssl s_client -connect localhost:443 -ssl3` (should fail)

## Modernized Role Structure

To properly modernize this into a role, the following structure should be created:

```yaml
# tasks/main.yml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    path: "{{ apache_ssl_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol {{ ssl_protocol_setting }}'
    mode: '0644'
  notify:
    - Restart apache2
    - Restart sshd

# handlers/main.yml
---
- name: Restart apache2
  ansible.builtin.service:
    name: apache2
    state: restarted

- name: Restart sshd
  ansible.builtin.service:
    name: sshd
    state: restarted

# defaults/main.yml
---
apache_ssl_config_path: /etc/apache2/mods-available/ssl.conf
ssl_protocol_setting: "-all +TLSv1.2"

# meta/main.yml
---
galaxy_info:
  role_name: poodle_fix
  author: your_name
  description: Mitigates POODLE vulnerability in Apache SSL configuration
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

# meta/argument_specs.yml
---
argument_specs:
  main:
    short_description: Mitigates POODLE vulnerability in Apache SSL configuration
    description:
      - Updates Apache SSL configuration to disable vulnerable protocols
      - Enables only TLSv1.2 to mitigate POODLE vulnerability
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