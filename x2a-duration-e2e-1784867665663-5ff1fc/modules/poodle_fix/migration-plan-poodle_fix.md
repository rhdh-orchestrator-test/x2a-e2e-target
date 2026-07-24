---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and provide a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This is a simple Ansible playbook (not a role) that mitigates the POODLE SSL vulnerability by updating Apache's SSL configuration to disable vulnerable protocols and enable only TLSv1.2. The playbook needs to be converted to a proper role structure with modernized syntax including fully qualified collection names (FQCN) and proper handler naming.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a role. We need to create a proper role structure.**

Proposed role structure:
```
tasks/main.yml
handlers/main.yml
meta/main.yml
README.md
```

**Task Files:**
- tasks/main.yml (to be created from playbook tasks)

**Handler Files:**
- handlers/main.yml (to be created from playbook handlers)

**Variable Files:**
- defaults/main.yml (to be created for configuration options)

**Meta:**
- meta/main.yml (to be created with role metadata)

**Templates:**
None in original playbook

**Static Files:**
None in original playbook

## Module Explanation

The role performs operations in this order:

1. **Security Hardening** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module without FQCN
   - Notifies handlers with inconsistent naming ("Restart apache2" in notification vs "Restart apache" in handler)
   - Legacy pattern: Missing FQCN for `replace` module

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent handler naming | poodle_fix.yml | "Restart apache2" notification vs "Restart apache" handler |
| Playbook structure | Role structure | poodle_fix.yml | Convert standalone playbook to proper role |
| Missing documentation | Add README.md | N/A | Document role purpose and variables |
| Missing meta | Add meta/main.yml | N/A | Add role metadata |
| Missing variable customization | Add defaults/main.yml | N/A | Make SSL protocol configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: core modules

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates in the original playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `ssl_protocols`: string, default: '-all +TLSv1.2', description: 'SSL/TLS protocols to enable/disable'
- `apache_ssl_conf_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- README.md

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Check current SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- After applying role, verify SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Test SSL connection with: `openssl s_client -connect localhost:443 -tls1_2`
- Verify vulnerable protocols are disabled: `openssl s_client -connect localhost:443 -ssl3` (should fail)

## Implementation Details

### tasks/main.yml
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: "{{ apache_ssl_conf_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "SSLProtocol {{ ssl_protocols }}"
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
# SSL/TLS protocols to enable/disable
ssl_protocols: "-all +TLSv1.2"

# Path to Apache SSL configuration file
apache_ssl_conf_path: "/etc/apache2/mods-available/ssl.conf"
```

### meta/main.yml
```yaml
---
galaxy_info:
  role_name: poodle_fix
  author: your_name
  description: Mitigates POODLE SSL vulnerability in Apache
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
    short_description: Mitigates POODLE SSL vulnerability in Apache
    description:
      - This role updates Apache SSL configuration to mitigate the POODLE vulnerability
      - Disables vulnerable SSL protocols and enables only secure TLS versions
    options:
      ssl_protocols:
        type: str
        default: "-all +TLSv1.2"
        description: SSL/TLS protocols to enable/disable
      apache_ssl_conf_path:
        type: str
        default: "/etc/apache2/mods-available/ssl.conf"
        description: Path to Apache SSL configuration file
```