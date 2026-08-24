---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This is a simple Ansible playbook that mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The playbook needs to be converted from a standalone playbook to a proper Ansible role structure with fully qualified collection names (FQCN), proper boolean syntax, and organized directory structure.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability by enforcing TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a role. We need to create a proper role structure.**

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
   - Notifies handlers to restart services
   - Modern equivalent: Use `ansible.builtin.replace` with proper quoting and mode specification

2. **Service Restart** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - One handler already uses FQCN (`ansible.builtin.service`)
   - Handler name mismatch: "Restart apache" vs "Restart apache2" in notification

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Missing `mode:` | Add `mode: preserve` | tasks/main.yml | File permissions |
| Handler name mismatch | Consistent handler names | handlers/main.yml | "Restart apache" vs "Restart apache2" in notification |
| Standalone playbook | Proper role structure | All files | Convert to role structure |
| Missing idempotency check | Add `changed_when` condition | tasks/main.yml | Ensure idempotency |
| Missing role metadata | Create meta/main.yml | meta/main.yml | Add proper role metadata |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the current playbook.

## Argument Specification

For meta/argument_specs.yml:
- `apache_ssl_config_path`: 
  - type: str
  - default: "/etc/apache2/mods-available/ssl.conf"
  - description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: 
  - type: str
  - default: "-all +TLSv1.2"
  - description: "SSL protocol settings to mitigate POODLE vulnerability"

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
```
# Verify Apache configuration syntax
apache2ctl configtest

# Check SSL/TLS protocols enabled
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify services are running
systemctl status apache2
systemctl status sshd
```