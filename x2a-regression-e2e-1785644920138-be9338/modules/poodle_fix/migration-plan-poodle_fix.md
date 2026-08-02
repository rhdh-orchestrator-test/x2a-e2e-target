---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This is a simple Ansible playbook that mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The playbook needs to be converted from a standalone playbook to a proper Ansible role structure with fully qualified collection names (FQCN), proper boolean syntax, and structured organization.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability by enforcing TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a role. We need to create a proper role structure.**

The current file:
```
poodle_fix.yml
```

The proposed role structure:
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
None identified in the source

**Static Files:**
None identified in the source

## Module Explanation

The role performs operations in this order:

1. **Security Hardening** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Legacy pattern: non-FQCN module name `replace:`
   - Modern equivalent: `ansible.builtin.replace:`
   - Notifies handlers to restart services after configuration changes

2. **Service Restart** (`handlers/main.yml`):
   - Contains handlers to restart Apache and SSH services
   - Apache handler already uses FQCN (`ansible.builtin.service`)
   - SSH handler uses FQCN but needs to be renamed to match the notification in tasks

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Standalone playbook | Role structure | All files | Convert to proper role structure |
| Handler name mismatch | Match handler names | handlers/main.yml | Handler "Restart apache" vs notification "Restart apache2" |
| Missing role metadata | Create meta/main.yml | meta/main.yml | Add proper role metadata |
| Missing documentation | Create README.md | README.md | Document role purpose and usage |
| Missing variable defaults | Create defaults/main.yml | defaults/main.yml | Define configurable variables |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required (only using builtin modules)

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the source.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `poodle_fix_apache_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'
- `poodle_fix_ssl_protocol`: string, default: '-all +TLSv1.2', description: 'SSL protocol configuration string'
- `poodle_fix_restart_apache`: boolean, default: true, description: 'Whether to restart Apache after configuration changes'
- `poodle_fix_restart_ssh`: boolean, default: true, description: 'Whether to restart SSH after configuration changes'

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
```bash
# Verify Apache configuration syntax
apache2ctl configtest

# Verify SSH configuration syntax
sshd -t

# Test SSL configuration
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify no SSLv3 (POODLE vulnerability) is enabled
openssl s_client -connect localhost:443 -ssl3
# Should fail with "ssl3 alert handshake failure" or similar
```