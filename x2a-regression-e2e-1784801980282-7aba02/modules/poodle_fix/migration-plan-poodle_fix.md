---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This is a simple Ansible playbook (not a role) that mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The playbook needs to be converted to a proper Ansible role structure with modernized syntax including FQCN module names, proper handler naming, and structured organization.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a role. We need to create a proper role structure.**

For the new role structure:
```
tasks/main.yml
handlers/main.yml
meta/main.yml
defaults/main.yml
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
None in original playbook

**Static Files:**
None in original playbook

## Module Explanation

The role performs operations in this order:

1. **Main Tasks** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the replace module to modify the SSL configuration file
   - Legacy pattern: short module name `replace:` without FQCN
   - Modern equivalent: `ansible.builtin.replace:`
   - Notifies handlers to restart services after configuration changes

2. **Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Already uses FQCN for service module (`ansible.builtin.service:`)
   - Handler name mismatch: Notified as "Restart apache2" but handler is named "Restart apache"

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Handler name mismatch | Consistent handler names | handlers/main.yml | Handler "Restart apache" should match notification "Restart apache2" |
| Playbook structure | Role structure | All files | Convert from standalone playbook to proper role structure |
| Missing `mode:` | Add `mode:` parameter | tasks/main.yml | For file operations (though not directly applicable in replace module) |
| Missing documentation | Add role documentation | README.md | Document role purpose, variables, and usage |
| Missing metadata | Add role metadata | meta/main.yml | Define role dependencies, supported platforms |
| Missing variable definitions | Define variables | defaults/main.yml | Extract hardcoded values to variables |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: core modules

**Role dependencies**: None
**External packages**: apache2, openssh-server (implied by service restarts)
**Services managed**: apache2, sshd

## Template Modernization

No templates in the original playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration changes"
- `restart_ssh`: boolean, default: true, description: "Whether to restart SSH after configuration changes"

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
- Check SSL configuration syntax: `apache2ctl configtest`
- Verify SSL settings after applying: `openssl s_client -connect localhost:443 -tls1_2`
- Test for POODLE vulnerability: `nmap --script ssl-poodle -p 443 localhost`

## Implementation Details

### tasks/main.yml
```yaml
---
- name: Fix SSL in Apache to mitigate POODLE vulnerability
  ansible.builtin.replace:
    dest: "{{ apache_ssl_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "{{ ssl_protocol_setting }}"
  notify:
    - Restart apache2
    - Restart sshd
  when: restart_apache | bool
```

### handlers/main.yml
```yaml
---
- name: Restart apache2
  ansible.builtin.service:
    name: apache2
    state: restarted
  when: restart_apache | bool

- name: Restart sshd
  ansible.builtin.service:
    name: sshd
    state: restarted
  when: restart_ssh | bool
```

### defaults/main.yml
```yaml
---
apache_ssl_config_path: "/etc/apache2/mods-available/ssl.conf"
ssl_protocol_setting: "SSLProtocol -all +TLSv1.2"
restart_apache: true
restart_ssh: true
```

### meta/main.yml
```yaml
---
galaxy_info:
  role_name: poodle_fix
  author: your_name
  description: Mitigates POODLE vulnerability in Apache SSL configuration
  license: MIT
  min_ansible_version: 2.9
  platforms:
    - name: Ubuntu
      versions:
        - all
    - name: Debian
      versions:
        - all
  galaxy_tags:
    - security
    - apache
    - ssl
    - poodle
    - hardening

dependencies: []
```