---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This playbook mitigates the POODLE vulnerability by updating SSL configurations in Apache to disable vulnerable protocols and enable only TLSv1.2. The modernization needs include converting to FQCN module names, updating handler names to match notification names, and restructuring the playbook into a proper Ansible role format.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a role. The migration will convert this to a proper role structure.**

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
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **Main Tasks** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Legacy pattern: Uses short-form module name `replace:` instead of FQCN
   - Modern equivalent: Convert to `ansible.builtin.replace:`
   - Ansible module mapping: `replace:` → `ansible.builtin.replace:`

2. **Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name "Restart apache" doesn't match notification name "Restart apache2"
   - Modern equivalent: Ensure handler names match notification names exactly
   - Ansible module mapping: Already using FQCN `ansible.builtin.service:`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler name to notification | poodle_fix.yml | "Restart apache" vs "Restart apache2" |
| Standalone playbook | Proper role structure | poodle_fix.yml | Convert to role with tasks/handlers/meta |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required, uses only builtin modules

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

Proposed variables for meta/argument_specs.yml:
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
- meta/main.yml
- defaults/main.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Validate Apache config after changes: `apache2ctl configtest`
- Check SSL configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify POODLE vulnerability is mitigated: `nmap --script ssl-enum-ciphers -p 443 localhost`