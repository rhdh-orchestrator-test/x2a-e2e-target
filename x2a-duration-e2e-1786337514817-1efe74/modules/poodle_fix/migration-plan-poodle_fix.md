---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL/TLS protocol configurations in Apache. It needs modernization primarily for FQCN module names, proper handler naming, and structural improvements to convert from a playbook format to a proper role structure.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook file, not a proper Ansible role. The migration will create a role structure.**

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
tasks/main.yml (to be created)

**Handler Files:**
handlers/main.yml (to be created)

**Variable Files:**
defaults/main.yml (to be created)

**Meta:**
meta/main.yml (to be created)

**Templates:**
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration Fix** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Legacy pattern: Uses short-form module name `replace:`
   - Modern equivalent: Use FQCN `ansible.builtin.replace:`
   - Ansible module mapping: `replace:` → `ansible.builtin.replace:`

2. **Service Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch (notify uses "Restart apache2" but handler is "Restart apache")
   - Modern equivalent: Ensure handler names match exactly with notify statements
   - Ansible module mapping: Already using FQCN `ansible.builtin.service:`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names exactly | poodle_fix.yml | "Restart apache2" in notify vs "Restart apache" in handler |
| Playbook format | Role structure | poodle_fix.yml | Convert standalone playbook to proper role structure |
| Missing `mode:` | Add `mode:` parameter | tasks/main.yml | File operations should specify mode for security |
| Missing role metadata | Create meta/main.yml | N/A | Add proper role metadata |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None (uses only builtin modules)

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

Proposed variables for meta/argument_specs.yml:
- `poodle_fix_apache_config_path`: 
  - Type: string
  - Default: "/etc/apache2/mods-available/ssl.conf"
  - Description: "Path to Apache SSL configuration file"
- `poodle_fix_ssl_protocol`: 
  - Type: string
  - Default: "-all +TLSv1.2"
  - Description: "SSL/TLS protocol configuration string"

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
- Check SSL/TLS configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify POODLE vulnerability is mitigated: `nmap --script ssl-enum-ciphers -p 443 localhost`