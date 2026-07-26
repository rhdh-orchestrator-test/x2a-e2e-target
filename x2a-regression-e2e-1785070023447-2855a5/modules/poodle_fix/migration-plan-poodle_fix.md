---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This is a simple Ansible playbook that mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The playbook needs to be converted from a standalone playbook to a proper Ansible role structure with modernized syntax including FQCN module names, proper handler naming, and structured organization.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability by restricting protocols to TLSv1.2
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

1. **SSL Configuration** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Legacy pattern: Uses short-form module name `replace:` without FQCN
   - Modern equivalent: `ansible.builtin.replace:`
   - Notifies handlers to restart services after configuration changes

2. **Service Restart Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch (defined as "Restart apache" but notified as "Restart apache2")
   - Modern equivalent: Consistent handler naming and FQCN module usage

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Handler name mismatch | Consistent handler naming | handlers/main.yml | "Restart apache" vs "Restart apache2" |
| Standalone playbook | Proper role structure | All files | Convert from playbook to role |
| Missing `mode:` parameter | Add `mode:` parameter for file operations | tasks/main.yml | Idempotency and security |
| Missing `changed_when` | Add `changed_when` condition | tasks/main.yml | For better idempotency reporting |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None identified, only uses builtin modules

**Role dependencies**: None identified
**External packages**: None directly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the current playbook.

## Argument Specification

Proposed variables for meta/argument_specs.yml:
- `poodle_fix_ssl_protocol`: string, default: '-all +TLSv1.2', description: "SSL protocols to enable/disable in Apache configuration"
- `poodle_fix_apache_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: "Path to Apache SSL configuration file"

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
- Verify SSL configuration file exists: `ls -la /etc/apache2/mods-available/ssl.conf`
- Validate Apache configuration after changes: `apache2ctl configtest`
- Test SSL configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify POODLE vulnerability is mitigated: `nmap --script ssl-enum-ciphers -p 443 localhost`