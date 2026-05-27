---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper handler names, and structured playbook organization.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**Task Files:**
chef-and-ansible/poodle_fix.yml (playbook with embedded tasks)

**Handler Files:**
chef-and-ansible/poodle_fix.yml (handlers embedded in playbook)

**Variable Files:**
None

**Meta:**
None

**Templates:**
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration Fix** (`chef-and-ansible/poodle_fix.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module without FQCN
   - Notifies two handlers: "Restart apache2" and "Restart sshd", but handler name "Restart apache2" doesn't match the defined handler "Restart apache"
   - Modern equivalent: Use `ansible.builtin.replace` with proper handler name matching

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names exactly | poodle_fix.yml | Handler "Restart apache2" in notify doesn't match "Restart apache" in handler definition |
| Playbook with embedded tasks | Convert to proper role structure | poodle_fix.yml | Create tasks/main.yml, handlers/main.yml |
| No mode specified for file operations | Add `mode:` parameter | poodle_fix.yml | File permissions should be explicitly set |
| No `changed_when` for idempotency | Add proper change detection | poodle_fix.yml | Ensure idempotent execution |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required for basic functionality

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache is already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the current role

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
- Verify Apache SSL configuration: `grep -r "SSLProtocol" /etc/apache2/`
- Check Apache syntax: `apache2ctl -t`
- Verify SSL/TLS settings: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Ensure services are running: `systemctl status apache2 && systemctl status sshd`

## Proposed Role Structure

The current file is a playbook with embedded tasks and handlers. It should be converted to a proper role structure:

```
roles/
└── poodle_fix/
    ├── tasks/
    │   └── main.yml
    ├── handlers/
    │   └── main.yml
    └── meta/
        └── main.yml
```

**tasks/main.yml**:
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: /etc/apache2/mods-available/ssl.conf
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol -all +TLSv1.2'
    mode: '0644'
  notify:
    - Restart apache
    - Restart sshd
```

**handlers/main.yml**:
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

**meta/main.yml**:
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