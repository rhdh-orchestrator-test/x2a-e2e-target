---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and fix handler naming inconsistencies.

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
   - Updates Apache SSL configuration to mitigate the POODLE vulnerability by replacing the SSLProtocol directive
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Sets SSLProtocol to disable all protocols except TLSv1.2
   - Notifies handlers to restart Apache and SSH services
   - Legacy patterns found: short module name `replace`, handler name inconsistency
   - Modern equivalent: Use FQCN `ansible.builtin.replace`, ensure handler names match notification names

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name inconsistency | Match handler names with notify names | poodle_fix.yml | Handler "Restart apache" doesn't match notify "Restart apache2" |
| Playbook structure | Convert to proper role structure | poodle_fix.yml | Convert from standalone playbook to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required for this simple role

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache is already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables are defined in this simple role

## Checks for the Migration

**Files to verify**:
- tasks/main.yml (to be created)
- handlers/main.yml (to be created)
- meta/main.yml (to be created)

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Check SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Validate Apache configuration: `apache2ctl configtest`

## Migration Steps

1. **Create proper role structure**:
   - Create directory structure: `tasks/`, `handlers/`, `meta/`
   - Move task from playbook to `tasks/main.yml`
   - Move handlers to `handlers/main.yml`
   - Create basic `meta/main.yml`

2. **tasks/main.yml**:
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: /etc/apache2/mods-available/ssl.conf
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol -all +TLSv1.2'
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

4. **meta/main.yml**:
```yaml
---
galaxy_info:
  author: Your Name
  description: Role to fix POODLE vulnerability in Apache
  company: Your Company
  license: license (GPL-2.0-or-later, MIT, etc)
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