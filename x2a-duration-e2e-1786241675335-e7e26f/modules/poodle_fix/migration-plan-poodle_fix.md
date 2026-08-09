---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This role implements a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for syntax updates, including fully qualified collection names (FQCN), proper handler naming, and structural improvements.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate the POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Notifies handlers to restart Apache and SSH services after configuration changes
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Fix handler name consistency | poodle_fix.yml | Handler name in notify ("Restart apache2") doesn't match handler name ("Restart apache") |
| Playbook structure | Convert to role structure | poodle_fix.yml | Convert from standalone playbook to proper role structure |
| Missing mode for file operations | Add mode parameter | poodle_fix.yml | Add mode parameter for file operations |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None
**Services managed**: apache2, sshd

## Template Modernization

No templates are present in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables are defined in this role that would need argument specifications.

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache configuration syntax: `apache2ctl configtest`
- Check SSL/TLS configuration: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify SSH configuration: `sshd -t`
- Test SSL/TLS security: `openssl s_client -connect localhost:443 -tls1_2`
- Verify POODLE vulnerability is mitigated: `openssl s_client -connect localhost:443 -ssl3` (should fail)

## Migration Steps

1. **Create proper role structure**:
   - Create directory structure for a proper Ansible role
   - Move tasks to tasks/main.yml
   - Move handlers to handlers/main.yml
   - Create meta/main.yml

2. **Update tasks/main.yml**:
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: /etc/apache2/mods-available/ssl.conf
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol -all +TLSv1.2'
    mode: '0644'
  notify:
    - Restart apache2
    - Restart sshd
```

3. **Create handlers/main.yml**:
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

4. **Create meta/main.yml**:
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