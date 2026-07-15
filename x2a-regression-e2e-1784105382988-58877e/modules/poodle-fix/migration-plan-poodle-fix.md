---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for syntax updates, including fully qualified collection names (FQCN) for the replace module and handler naming consistency.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 protocol
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Connects to target hosts as root with privilege escalation
   - Updates Apache SSL configuration to mitigate the POODLE vulnerability by replacing the SSLProtocol directive
   - Notifies handlers to restart Apache and SSH services
   - Legacy pattern: Uses short module name `replace` instead of FQCN
   - Modern equivalent: Should use `ansible.builtin.replace`
   - Handler name inconsistency: Task notifies "Restart apache2" but handler is named "Restart apache"

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | Task notifies "Restart apache2" but handler is named "Restart apache" |
| No `changed_when` for idempotency | Add `changed_when` condition | poodle_fix.yml | Improve idempotency tracking |
| No mode specified for file operations | Add mode parameter | poodle_fix.yml | Security best practice |

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
- Test SSL vulnerability: `openssl s_client -connect localhost:443 -ssl3`

## Recommended Structure for Migration

This playbook should be converted to a proper Ansible role structure:

1. Create standard role directory structure:
   - tasks/main.yml
   - handlers/main.yml
   - meta/main.yml

2. Move the task to tasks/main.yml with FQCN:
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

3. Move handlers to handlers/main.yml with consistent naming:
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

4. Create meta/main.yml:
```yaml
---
galaxy_info:
  author: Your Name
  description: Role to fix POODLE SSL vulnerability in Apache
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