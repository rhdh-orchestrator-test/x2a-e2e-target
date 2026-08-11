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

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

```
poodle_fix.yml
```

**Task Files:**
poodle_fix.yml (contains inline tasks)

**Handler Files:**
poodle_fix.yml (contains inline handlers)

**Variable Files:**
None

**Meta:**
None

**Templates:**
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **Main tasks** (`poodle_fix.yml`):
   - Updates Apache SSL configuration to mitigate POODLE vulnerability
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Changes the SSLProtocol directive to only allow TLSv1.2
   - Notifies handlers to restart Apache and SSH services
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Handlers** (`poodle_fix.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Uses the `service` module to restart services
   - Ansible module mapping: One handler already uses `ansible.builtin.service`, the other needs updating

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `service:` | `ansible.builtin.service:` | poodle_fix.yml | FQCN (one handler already modernized) |
| Handler name inconsistency | Consistent handler names | poodle_fix.yml | Handler name "Restart apache" doesn't match notification "Restart apache2" |
| `yes` | `true` | poodle_fix.yml | Boolean syntax |
| Playbook structure | Role structure | poodle_fix.yml | Convert from playbook to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: core

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the current playbook, but could add:
  - `ssl_protocol`: string, default: '-all +TLSv1.2', description: "SSL protocols to enable/disable"
  - `apache_conf_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: "Path to Apache SSL configuration file"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- meta/argument_specs.yml
- defaults/main.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
```
# Verify Apache configuration syntax
apache2ctl configtest

# Check SSL/TLS configuration
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify SSH configuration
sshd -t

# Test for POODLE vulnerability
openssl s_client -connect localhost:443 -ssl3
# Should fail with "ssl3 alert handshake failure" if properly secured
```