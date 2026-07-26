---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for syntax updates, including fully qualified collection names (FQCN) for the replace module and handler notification consistency.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate the POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a playbook, not a role. The migration plan will convert this playbook into a proper Ansible role structure.**

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
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart services
   - Modern equivalent: Use `ansible.builtin.replace` with proper handler names

2. **Service Restart Handlers** (`handlers/main.yml`):
   - Contains handlers to restart Apache and SSH services
   - Uses FQCN for the service module (`ansible.builtin.service`)
   - Handler name mismatch: "Restart apache" vs "Restart apache2" in notification
   - Modern equivalent: Ensure handler names match notifications exactly

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Handler name mismatch | Match handler names with notifications | handlers/main.yml | "Restart apache" vs "Restart apache2" |
| Playbook structure | Role structure | All files | Convert from playbook to role |
| Missing mode parameter | Add `mode:` parameter for file operations | tasks/main.yml | Best practice for file operations |
| Missing role metadata | Create meta/main.yml | meta/main.yml | Add proper role metadata |
| Missing variable defaults | Create defaults/main.yml | defaults/main.yml | Parameterize configuration |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None (only uses ansible.builtin modules)

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default: "-all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration change"
- `restart_ssh`: boolean, default: true, description: "Whether to restart SSH after configuration change"

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

# Check SSL/TLS configuration
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify SSH configuration
sshd -t

# Check for POODLE vulnerability
openssl s_client -connect localhost:443 -ssl3
# Should fail with "wrong version number" if properly configured
```