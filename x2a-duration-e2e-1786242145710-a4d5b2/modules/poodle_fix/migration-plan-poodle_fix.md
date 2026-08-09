---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This playbook mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The modernization needs include converting to a proper role structure, using FQCN for modules, fixing handler names, and implementing proper boolean syntax.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a role. The migration will create a proper role structure.**

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
- tasks/main.yml

**Handler Files:**
- handlers/main.yml

**Variable Files:**
- defaults/main.yml (to be created)

**Meta:**
- meta/main.yml (to be created)

**Templates:**
- None

**Static Files:**
- None

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration Update** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Legacy pattern: Uses short module name `replace` without FQCN
   - Modern equivalent: Use `ansible.builtin.replace` with proper parameter formatting
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch (defined as "Restart apache" but notified as "Restart apache2")
   - Modern equivalent: Ensure handler names match notification names exactly
   - Ansible module mapping: Already using FQCN `ansible.builtin.service`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Handler name mismatch | Match handler name to notification | handlers/main.yml | "Restart apache" vs "Restart apache2" |
| Playbook structure | Role structure | All files | Convert standalone playbook to proper role |
| Missing `mode` parameter | Add `mode` parameter | tasks/main.yml | For file operations |
| Missing role metadata | Create meta/main.yml | meta/main.yml | Add proper role metadata |
| Missing variable defaults | Create defaults/main.yml | defaults/main.yml | Define configurable variables |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None (only uses builtin modules)

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default: "-all +TLSv1.2", description: "SSL protocol settings to mitigate POODLE vulnerability"

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
- Validate Apache configuration after changes: `apache2ctl configtest`
- Check SSL configuration: `grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf`
- Verify TLS version with: `nmap --script ssl-enum-ciphers -p 443 localhost`