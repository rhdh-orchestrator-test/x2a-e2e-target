---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper handler names, and structured playbook organization.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Updates Apache SSL configuration to mitigate the POODLE vulnerability by replacing the SSLProtocol line to only allow TLSv1.2
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart Apache and SSH services
   - Handler names in notification don't match actual handler names (inconsistency)
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names | poodle_fix.yml | Notification "Restart apache2" doesn't match handler "Restart apache" |
| Playbook structure | Convert to role structure | poodle_fix.yml | Convert from playbook to proper role structure |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean modernization |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None explicitly required

**Role dependencies**: None
**External packages**: None explicitly installed
**Services managed**: apache2, sshd

## Template Modernization

No templates present in the current structure.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the current playbook

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
- Verify Apache configuration: `apache2ctl configtest`
- Check SSL/TLS protocols: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify SSH configuration: `sshd -t`
- Test SSL vulnerability: `openssl s_client -connect localhost:443 -ssl3`

## Migration Steps

1. **Create proper role structure**:
   - Create directory structure for a proper Ansible role
   - Move tasks to tasks/main.yml
   - Move handlers to handlers/main.yml
   - Create meta/main.yml

2. **Tasks file (tasks/main.yml)**:
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: /etc/apache2/mods-available/ssl.conf
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol -all +TLSv1.2'
  notify:
    - Restart apache
    - Restart sshd
```

3. **Handlers file (handlers/main.yml)**:
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

4. **Meta file (meta/main.yml)**:
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