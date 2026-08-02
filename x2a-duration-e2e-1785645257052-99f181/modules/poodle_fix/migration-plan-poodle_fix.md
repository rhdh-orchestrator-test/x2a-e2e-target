---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper handler naming, and structured organization into a standard Ansible role format.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate the POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a structured Ansible role. The migration will convert this into a proper role structure.**

Current file:
```
chef-and-ansible/poodle_fix.yml
```

Proposed role structure after migration:
```
tasks/main.yml
handlers/main.yml
meta/main.yml
README.md
meta/argument_specs.yml
```

**Task Files:**
tasks/main.yml

**Handler Files:**
handlers/main.yml

**Variable Files:**
defaults/main.yml

**Meta:**
meta/main.yml
meta/argument_specs.yml

**Templates:**
None identified in the current playbook

**Static Files:**
None identified in the current playbook

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration Update** (`tasks/main.yml`):
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart services after configuration changes
   - Modern equivalent: Use `ansible.builtin.replace` with proper mode specification

2. **Service Restart Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Uses `ansible.builtin.service` for Apache but lacks FQCN consistency
   - Modern equivalent: Use consistent FQCN for all service handlers

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN modernization |
| Missing `mode:` parameter | Add `mode: preserve` | poodle_fix.yml | File permissions best practice |
| Handler name mismatch | Consistent handler naming | poodle_fix.yml | Handler "Restart apache2" is notified but defined as "Restart apache" |
| Standalone playbook | Structured role | poodle_fix.yml | Convert to proper role structure |
| Missing `changed_when` | Add proper change detection | poodle_fix.yml | Improve idempotency |
| Missing role metadata | Add `meta/main.yml` | N/A | Add proper role metadata |
| Missing argument specs | Add `meta/argument_specs.yml` | N/A | Document role parameters |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None identified
**External packages**: None directly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the current playbook.

## Argument Specification

Document variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default: "-all +TLSv1.2", description: "SSL protocol settings to mitigate POODLE vulnerability"

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
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Validate Apache configuration after changes: `apache2ctl configtest`
- Test SSL configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify POODLE vulnerability is mitigated: `nmap --script ssl-enum-ciphers -p 443 localhost`

## Implementation Details

### tasks/main.yml
```yaml
---
- name: Fix SSL in Apache to mitigate POODLE vulnerability
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
apache_ssl_config_path: /etc/apache2/mods-available/ssl.conf
ssl_protocol_setting: "-all +TLSv1.2"
```

### meta/main.yml
```yaml
---
galaxy_info:
  role_name: poodle_fix
  author: your_name
  description: Role to mitigate POODLE vulnerability in Apache SSL configuration
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
    - hardening
dependencies: []
```

### meta/argument_specs.yml
```yaml
---
argument_specs:
  main:
    short_description: Role to mitigate POODLE vulnerability in Apache SSL configuration
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