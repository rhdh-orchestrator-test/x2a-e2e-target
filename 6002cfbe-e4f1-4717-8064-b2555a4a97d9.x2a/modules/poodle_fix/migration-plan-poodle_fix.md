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

**IMPORTANT: The provided file is a standalone playbook, not a structured Ansible role.**

poodle_fix.yml

## Module Explanation

The playbook performs operations in this order:

1. **poodle_fix.yml**:
   - Targets hosts in the 'myhost' group with root privileges
   - Uses the replace module to modify Apache SSL configuration
   - Updates the SSLProtocol directive to disable all protocols except TLSv1.2
   - Notifies handlers to restart Apache and SSH services
   - Ansible module mapping: `replace:` → `ansible.builtin.replace:`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `yes` | `true` | poodle_fix.yml | Boolean modernization |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | Handler "Restart apache2" is notified but defined as "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are present in this playbook.

## Argument Specification

Since this is a standalone playbook rather than a role, argument specifications would be implemented differently. If converting to a role, the following variables should be considered:

- `apache_ssl_config_path`: String, default: '/etc/apache2/mods-available/ssl.conf', path to Apache SSL configuration
- `ssl_protocol_setting`: String, default: '-all +TLSv1.2', SSL protocol configuration

## Checks for the Migration

**Files to verify**: 
- poodle_fix.yml (modernized)

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Validate Apache configuration: `apache2ctl configtest`
- Check SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Verify TLS version with: `nmap --script ssl-enum-ciphers -p 443 localhost`

## Conversion to Proper Role Structure

To convert this standalone playbook to a proper Ansible role, the following structure should be created:

```
roles/poodle_fix/
├── defaults/
│   └── main.yml       # Default variables
├── handlers/
│   └── main.yml       # Handlers for service restarts
├── meta/
│   └── main.yml       # Role metadata
├── tasks/
│   └── main.yml       # Main tasks
└── README.md          # Role documentation
```

**tasks/main.yml** would contain:
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: "{{ apache_ssl_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "SSLProtocol {{ ssl_protocol_setting }}"
  notify:
    - Restart apache2
    - Restart sshd
```

**handlers/main.yml** would contain:
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

**defaults/main.yml** would contain:
```yaml
---
apache_ssl_config_path: /etc/apache2/mods-available/ssl.conf
ssl_protocol_setting: "-all +TLSv1.2"
```