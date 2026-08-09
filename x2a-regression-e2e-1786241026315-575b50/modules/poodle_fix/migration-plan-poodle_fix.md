---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for FQCN module names, handler naming consistency, and proper structure as a standalone Ansible role.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a properly structured role. The migration will create a proper role structure.**

Current file:
```
chef-and-ansible/poodle_fix.yml
```

Proposed role structure:
```
tasks/main.yml
handlers/main.yml
meta/main.yml
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
None identified

**Static Files:**
None identified

## Module Explanation

The role performs operations in this order:

1. **Security Hardening** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart services after configuration changes
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Restart** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Uses the `ansible.builtin.service` module for Apache but lacks FQCN for SSH
   - Handler name inconsistency: "Restart apache" vs "Restart apache2" in notification
   - Ansible module mapping: `service` → `ansible.builtin.service`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `service:` | `ansible.builtin.service:` | poodle_fix.yml | FQCN for SSH handler |
| Handler name inconsistency | Consistent handler names | poodle_fix.yml | Handler "Restart apache" is notified as "Restart apache2" |
| Playbook format | Role structure | poodle_fix.yml | Convert standalone playbook to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- No external collections required, only ansible.builtin modules are used

**Role dependencies**: None identified
**External packages**: None directly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the current playbook.

## Argument Specification

Proposed variables for meta/argument_specs.yml:
- `poodle_fix_apache_config_path`: 
  - Type: string
  - Default: "/etc/apache2/mods-available/ssl.conf"
  - Description: "Path to Apache SSL configuration file"
- `poodle_fix_ssl_protocol`: 
  - Type: string
  - Default: "-all +TLSv1.2"
  - Description: "SSL protocol configuration string for Apache"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- defaults/main.yml
- README.md

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Validate Apache configuration after changes: `apache2ctl configtest`
- Check SSL configuration: `grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf`
- Verify TLS version with: `nmap --script ssl-enum-ciphers -p 443 localhost`