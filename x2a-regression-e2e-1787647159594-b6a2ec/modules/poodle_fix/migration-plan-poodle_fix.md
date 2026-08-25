---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role implements a security fix for the POODLE vulnerability by updating SSL/TLS protocol settings in Apache. It needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and structured handlers with consistent naming.

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
   - Updates Apache SSL configuration to mitigate the POODLE vulnerability by restricting protocols to TLSv1.2
   - Legacy patterns found: non-FQCN module names (`replace`), inconsistent handler naming
   - Modern equivalent: Use `ansible.builtin.replace` with proper handler naming
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name inconsistency (`Restart apache2` in notify vs `Restart apache` in handler) | Consistent handler naming | poodle_fix.yml | Handler names should match exactly |
| Playbook structure | Role structure | poodle_fix.yml | Convert from playbook to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required (only uses builtin modules)

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates present in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the current playbook

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
- Verify Apache configuration syntax: `apache2ctl configtest`
- Check TLS protocol settings: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify SSH configuration: `sshd -t`
- Check SSH protocol settings: `nmap --script ssh2-enum-algos -p 22 localhost`

## Migration Implementation Plan

1. **Create proper role structure**:
   - Create directory structure: `tasks/`, `handlers/`, `meta/`, etc.
   - Move tasks to `tasks/main.yml`
   - Move handlers to `handlers/main.yml`
   - Create `meta/main.yml` with role metadata

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