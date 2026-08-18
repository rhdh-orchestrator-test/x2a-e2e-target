---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan for this Ansible role.

# Migration Plan: poodle_fix

**TLDR**: This role implements a security fix for the POODLE vulnerability by updating SSL/TLS protocol settings in Apache. It needs modernization from a playbook format to a proper Ansible role structure with fully qualified collection names (FQCN), proper handler naming, and modern syntax patterns.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a proper role structure. The migration will create a new role structure.**

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

1. **Main Tasks** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Legacy pattern: Uses short-form module name `replace:` instead of FQCN
   - Modern equivalent: `ansible.builtin.replace:`
   - Ansible module mapping: `replace:` → `ansible.builtin.replace:`

2. **Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch between task notification and handler definition
   - Modern equivalent: Consistent handler naming
   - Ansible module mapping: Already using FQCN `ansible.builtin.service:`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent handler naming | poodle_fix.yml | Task notifies "Restart apache2" but handler is named "Restart apache" |
| Playbook format | Role structure | poodle_fix.yml | Convert standalone playbook to proper role structure |
| Missing documentation | Add README.md | N/A | Document role purpose and variables |
| Missing meta | Add meta/main.yml | N/A | Add role metadata |
| Missing defaults | Add defaults/main.yml | N/A | Add configurable variables |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None (uses only builtin modules)

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'
- `ssl_protocol_setting`: string, default: '-all +TLSv1.2', description: 'SSL/TLS protocol settings for Apache'
- `restart_apache`: boolean, default: true, description: 'Whether to restart Apache after configuration changes'
- `restart_ssh`: boolean, default: true, description: 'Whether to restart SSH after configuration changes'

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
```bash
# Verify Apache configuration syntax
apache2ctl configtest

# Check SSL/TLS protocol settings
openssl s_client -connect localhost:443 -tls1_2

# Verify SSH configuration
sshd -t

# Check for POODLE vulnerability
nmap --script ssl-enum-ciphers -p 443 localhost
```