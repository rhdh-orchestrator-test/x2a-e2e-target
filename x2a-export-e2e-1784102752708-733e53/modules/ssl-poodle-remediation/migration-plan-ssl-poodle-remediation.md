---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: ssl-poodle-remediation

**TLDR**: This role mitigates the SSL POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The modernization needs include converting to FQCN module names, updating handler references, and structuring as a proper Ansible role.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 to mitigate POODLE vulnerability
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The current implementation is a standalone playbook, not a proper role. The migration will convert this to a role structure.**

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

1. **SSL Configuration Update** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable protocols and enable only TLSv1.2
   - Legacy pattern: Uses short module name `replace` without FQCN
   - Modern equivalent: Use `ansible.builtin.replace` with proper parameters
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch between task notification and handler definition
   - Modern equivalent: Consistent handler names and FQCN for service module
   - Ansible module mapping: `ansible.builtin.service` is already used (modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | Task notifies "Restart apache2" but handler is named "Restart apache" |
| Playbook structure | Role structure | poodle_fix.yml | Convert standalone playbook to proper role structure |
| Missing `mode:` | Add `mode:` parameter | tasks/main.yml | File operations should specify mode for security |
| Missing role metadata | Create meta/main.yml | N/A | Add proper role metadata |
| Missing documentation | Create README.md | N/A | Document role purpose and variables |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None (uses only builtin modules)

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this role.

## Argument Specification

Proposed variables for meta/argument_specs.yml:
- `ssl_poodle_apache_config_path`: 
  - Type: string
  - Default: "/etc/apache2/mods-available/ssl.conf"
  - Description: "Path to Apache SSL configuration file"
- `ssl_poodle_protocol_string`: 
  - Type: string
  - Default: "-all +TLSv1.2"
  - Description: "SSL protocol string to use in Apache configuration"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- defaults/main.yml
- README.md

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
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: "{{ ssl_poodle_apache_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol {{ ssl_poodle_protocol_string }}'
    mode: '0644'
  notify:
    - Restart apache
    - Restart sshd
```

### handlers/main.yml
```yaml
---
- name: Restart apache
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
ssl_poodle_apache_config_path: "/etc/apache2/mods-available/ssl.conf"
ssl_poodle_protocol_string: "-all +TLSv1.2"
```

### meta/main.yml
```yaml
---
galaxy_info:
  role_name: ssl_poodle_remediation
  author: Your Name
  description: Role to mitigate SSL POODLE vulnerability in Apache
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
    short_description: Role to mitigate SSL POODLE vulnerability in Apache
    description:
      - This role updates Apache SSL configuration to disable vulnerable protocols
      - Enables only TLSv1.2 to mitigate POODLE vulnerability
    options:
      ssl_poodle_apache_config_path:
        type: str
        default: "/etc/apache2/mods-available/ssl.conf"
        description: Path to Apache SSL configuration file
      ssl_poodle_protocol_string:
        type: str
        default: "-all +TLSv1.2"
        description: SSL protocol string to use in Apache configuration
```