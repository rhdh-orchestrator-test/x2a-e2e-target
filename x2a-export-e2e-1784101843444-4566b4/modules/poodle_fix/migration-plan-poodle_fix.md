---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role implements a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The modernization needs include converting to FQCN module names, fixing handler names, and restructuring the playbook into a proper Ansible role format.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate the POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a proper Ansible role. The migration will convert this to a role structure.**

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
- tasks/main.yml (to be created)

**Handler Files:**
- handlers/main.yml (to be created)

**Variable Files:**
- defaults/main.yml (to be created)

**Meta:**
- meta/main.yml (to be created)

**Templates:**
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration Fix** (`tasks/main.yml`):
   - Updates the Apache SSL configuration to disable vulnerable SSL protocols
   - Uses the `replace` module without FQCN
   - Legacy pattern: missing FQCN for module name
   - Modern equivalent: Use `ansible.builtin.replace`
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Uses `ansible.builtin.service` for Apache but handler name doesn't match notification
   - Legacy pattern: Handler name mismatch (notifies "Restart apache2" but handler is "Restart apache")
   - Modern equivalent: Ensure handler names match exactly with notifications

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names with notifications | poodle_fix.yml | "Restart apache2" notification but "Restart apache" handler |
| Playbook format | Role structure | poodle_fix.yml | Convert standalone playbook to proper role structure |
| Missing `mode` parameter | Add `mode` parameter for file operations | tasks/main.yml | Best practice for file operations |
| Missing `changed_when` | Not applicable | N/A | No command/shell modules used |

## Dependencies

**Collection dependencies** (for requirements.yml):
- No external collections required, only ansible.builtin modules are used

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this role.

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