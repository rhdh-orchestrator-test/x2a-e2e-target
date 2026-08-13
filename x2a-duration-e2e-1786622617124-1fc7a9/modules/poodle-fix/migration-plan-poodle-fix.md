---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file I found:

# Migration Plan: poodle-fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and to fix handler naming inconsistencies.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a structured Ansible role.**

poodle_fix.yml

## Module Explanation

The playbook performs operations in this order:

1. **poodle_fix.yml**:
   - Targets hosts in the "myhost" group with root privileges
   - Uses the `replace` module to modify Apache SSL configuration, disabling vulnerable SSL protocols and enabling only TLSv1.2
   - Notifies handlers to restart Apache and SSH services after the configuration change
   - Legacy patterns found: non-FQCN module names, handler name inconsistency
   - Modern equivalent: Use FQCN for modules, ensure handler names match notification names

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean syntax |
| Handler name inconsistency: notifies "Restart apache2" but handler is "Restart apache" | Make handler name match notification: "Restart apache2" | poodle_fix.yml | Handler naming consistency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are present in this playbook.

## Argument Specification

Since this is a standalone playbook rather than a role, argument specifications are not applicable. If converting to a role, the following variables could be defined:

- ssl_protocol_string: String, default: '-all +TLSv1.2', description: "SSL protocols to enable/disable"
- apache_ssl_conf_path: String, default: '/etc/apache2/mods-available/ssl.conf', description: "Path to Apache SSL configuration file"

## Checks for the Migration

**Files to verify**: poodle_fix.yml (modernized)
**Services to check**: apache2, sshd
**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify Apache is running with updated configuration
apache2ctl -t
systemctl status apache2

# Verify SSH is running
systemctl status sshd

# Test SSL/TLS configuration
nmap --script ssl-enum-ciphers -p 443 localhost
```

## Conversion to Modern Ansible Role Structure

Since the original is a standalone playbook rather than a role, here's how it should be structured as a modern Ansible role:

```
roles/
└── poodle_fix/
    ├── defaults/
    │   └── main.yml       # Define default variables
    ├── handlers/
    │   └── main.yml       # Define handlers
    ├── meta/
    │   └── main.yml       # Role metadata
    ├── tasks/
    │   └── main.yml       # Define tasks
    └── README.md          # Role documentation
```

The modernized task file would contain:

```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: "{{ apache_ssl_conf_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "SSLProtocol {{ ssl_protocol_string }}"
  notify:
    - Restart apache2
    - Restart sshd
```

The modernized handler file would contain:

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