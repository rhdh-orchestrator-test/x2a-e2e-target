---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and provide a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This is a simple Ansible playbook that mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The playbook needs to be converted from a standalone playbook to a proper Ansible role structure with modernized syntax including FQCN module names, proper handler naming, and structured organization.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a role. The migration will create a proper role structure.**

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
None identified in the source

**Static Files:**
None identified in the source

## Module Explanation

The role performs operations in this order:

1. **Security Hardening** (`tasks/main.yml`):
   - Updates Apache SSL configuration to mitigate POODLE vulnerability by restricting SSL protocols
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart services
   - Modern equivalent: Use `ansible.builtin.replace` with proper mode specification

2. **Service Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Handler name mismatch: "Restart apache" vs "Restart apache2" in notification
   - Modern equivalent: Consistent handler naming and FQCN for service module

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Missing `mode:` | Add `mode: preserve` | tasks/main.yml | File permissions |
| Handler name mismatch | Consistent handler naming | handlers/main.yml | "Restart apache" vs "Restart apache2" in notification |
| Standalone playbook | Proper role structure | All files | Convert to role structure |
| Missing `changed_when` | Add idempotency controls | tasks/main.yml | For better idempotency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None identified, uses only builtin modules

**Role dependencies**: None identified
**External packages**: None directly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the source.

## Argument Specification

Proposed variables for meta/argument_specs.yml:
- `poodle_fix_ssl_protocol`: 
  - Type: string
  - Default: '-all +TLSv1.2'
  - Description: SSL protocol configuration string for Apache
- `poodle_fix_apache_config_path`:
  - Type: string
  - Default: '/etc/apache2/mods-available/ssl.conf'
  - Description: Path to Apache SSL configuration file

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
- Verify SSL configuration file exists: `ls -la /etc/apache2/mods-available/ssl.conf`
- Test Apache configuration after changes: `apache2ctl configtest`
- Verify SSL protocols after changes: `openssl s_client -connect localhost:443 -tls1_2`

## Implementation Details

### tasks/main.yml
```yaml
---
- name: Fix SSL in Apache to mitigate POODLE vulnerability
  ansible.builtin.replace:
    path: "{{ poodle_fix_apache_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol {{ poodle_fix_ssl_protocol }}'
    mode: preserve
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
poodle_fix_ssl_protocol: '-all +TLSv1.2'
poodle_fix_apache_config_path: '/etc/apache2/mods-available/ssl.conf'
```

### meta/main.yml
```yaml
---
galaxy_info:
  role_name: poodle_fix
  author: your_name
  description: Role to mitigate POODLE vulnerability in Apache
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
    short_description: Role to mitigate POODLE vulnerability in Apache
    description:
      - This role updates Apache SSL configuration to disable vulnerable SSL protocols
      - and enable only TLSv1.2 to mitigate the POODLE vulnerability
    options:
      poodle_fix_ssl_protocol:
        type: str
        default: '-all +TLSv1.2'
        description: SSL protocol configuration string for Apache
      poodle_fix_apache_config_path:
        type: str
        default: '/etc/apache2/mods-available/ssl.conf'
        description: Path to Apache SSL configuration file
```