---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This playbook mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The modernization needs include converting to FQCN module names, updating handler names to match notification names, and restructuring into a proper Ansible role format.

## Service Type and Configuration

**Service Type**: Web Server Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**Task Files:**
- chef-and-ansible/poodle_fix.yml (currently a standalone playbook, not a role)

**Handler Files:**
- Handlers are defined within the playbook (not in separate files)

**Variable Files:**
- None present

**Meta:**
- None present

**Templates:**
- None present

**Static Files:**
- None present

## Module Explanation

The playbook performs operations in this order:

1. **SSL Configuration Update** (`chef-and-ansible/poodle_fix.yml`):
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols
   - Uses the `replace` module without FQCN
   - Notifies handlers with name mismatch ("Restart apache2" vs "Restart apache")
   - Modern equivalent would use `ansible.builtin.replace` and consistent handler names

2. **Service Restart Handlers** (`chef-and-ansible/poodle_fix.yml`):
   - Contains handlers to restart Apache and SSH services
   - Apache handler uses FQCN (`ansible.builtin.service`) but SSH handler doesn't
   - Handler name "Restart apache" doesn't match the notification "Restart apache2"

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `service:` | `ansible.builtin.service:` | poodle_fix.yml | FQCN (already used for Apache handler) |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | "Restart apache" vs "Restart apache2" notification |
| Standalone playbook | Proper role structure | poodle_fix.yml | Convert to role with tasks/main.yml and handlers/main.yml |
| No argument specs | Add meta/argument_specs.yml | N/A | Define role parameters |
| No role metadata | Add meta/main.yml | N/A | Define role metadata |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: core modules

**Role dependencies**: None identified
**External packages**: None directly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates present in the current playbook.

## Argument Specification

For meta/argument_specs.yml:
- `apache_ssl_config_path`: 
  - Type: string
  - Default: "/etc/apache2/mods-available/ssl.conf"
  - Description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: 
  - Type: string
  - Default: "-all +TLSv1.2"
  - Description: "SSL protocol configuration string for Apache"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

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

# Verify SSH configuration
sshd -t

# Test for POODLE vulnerability
openssl s_client -connect localhost:443 -ssl3
# Should fail with "ssl3 alert handshake failure" if properly mitigated
```