---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan for this Ansible role.

# Migration Plan: poodle_fix

**TLDR**: This role mitigates the POODLE vulnerability by updating SSL/TLS protocol configurations in Apache. It needs modernization primarily for module syntax (FQCN), handler naming consistency, and proper idempotency checks.

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
   - Updates the Apache SSL configuration file to mitigate the POODLE vulnerability by restricting SSL/TLS protocols
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Sets `SSLProtocol -all +TLSv1.2` to disable all protocols except TLSv1.2
   - Notifies handlers to restart Apache and SSH services after the change
   - Legacy patterns found: short module name `replace`, missing FQCN for modules, handler name inconsistency
   - Modern equivalent: Use FQCN `ansible.builtin.replace`, ensure handler names match notification names

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name inconsistency | Match handler names with notify names | poodle_fix.yml | Handler "Restart apache" doesn't match notify "Restart apache2" |
| Missing `changed_when` | Add proper change detection | poodle_fix.yml | Ensure idempotency |
| Missing `mode` parameter | Add file permissions | poodle_fix.yml | Best practice for file operations |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables are defined in this playbook that would require argument specifications

## Checks for the Migration

**Files to verify**: 
- poodle_fix.yml (modernized)
- meta/main.yml (to be created)
- meta/argument_specs.yml (to be created if variables are added)

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache configuration syntax: `apache2ctl configtest`
- Check SSL/TLS configuration: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify SSH configuration: `sshd -t`
- Test TLS connection: `openssl s_client -connect localhost:443 -tls1_2`

## Modernized Role Structure

To properly convert this playbook into a role, the following structure should be created:

```yaml
# tasks/main.yml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    path: /etc/apache2/mods-available/ssl.conf
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol -all +TLSv1.2'
    mode: '0644'
  register: ssl_config_update
  changed_when: ssl_config_update.changed
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

# meta/main.yml
---
galaxy_info:
  author: Your Name
  description: Role to mitigate POODLE vulnerability in Apache
  company: Your Company
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