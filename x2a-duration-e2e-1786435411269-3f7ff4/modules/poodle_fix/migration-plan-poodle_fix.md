---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and create a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for FQCN module names, handler naming consistency, and proper structure as a standalone Ansible role.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a playbook, not a properly structured role. The migration will convert this to a proper role structure.**

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
tasks/main.yml (to be created)

**Handler Files:**
handlers/main.yml (to be created)

**Variable Files:**
defaults/main.yml (to be created)

**Meta:**
meta/main.yml (to be created)

**Templates:**
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Legacy pattern: Uses short-form module name `replace:`
   - Modern equivalent: Use FQCN `ansible.builtin.replace:`
   - Notifies handlers to restart services after configuration changes

2. **Service Restart Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name inconsistency ("Restart apache" vs "Restart apache2" in notification)
   - Modern equivalent: Ensure handler names match notification names exactly

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Handler name inconsistency | Match handler names with notifications | handlers/main.yml | Handler "Restart apache" should be "Restart apache2" to match notification |
| Playbook structure | Role structure | All files | Convert from single playbook to proper role structure |
| Missing `mode:` parameter | Add `mode:` parameter for file operations | tasks/main.yml | Best practice for security |
| Missing role metadata | Create proper meta/main.yml | meta/main.yml | Add proper role metadata |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

For meta/argument_specs.yml:
- `apache_config_path`: 
  - type: str
  - default: "/etc/apache2/mods-available/ssl.conf"
  - description: "Path to Apache SSL configuration file"
- `ssl_protocol_string`: 
  - type: str
  - default: "-all +TLSv1.2"
  - description: "SSL protocol configuration string"

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
    dest: "{{ apache_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol {{ ssl_protocol_string }}'
    mode: '0644'
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
apache_config_path: "/etc/apache2/mods-available/ssl.conf"
ssl_protocol_string: "-all +TLSv1.2"
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
      - Enables only TLSv1.2 to mitigate the POODLE vulnerability
    options:
      apache_config_path:
        type: str
        default: "/etc/apache2/mods-available/ssl.conf"
        description: Path to Apache SSL configuration file
      ssl_protocol_string:
        type: str
        default: "-all +TLSv1.2"
        description: SSL protocol configuration string
```