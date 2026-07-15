---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The modernization needs include converting to FQCN module names, fixing handler names, and restructuring the playbook into a proper Ansible role format.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a proper role structure. The migration will create a role with the following structure:**

```
tasks/main.yml
handlers/main.yml
meta/main.yml
README.md
```

**Task Files:**
tasks/main.yml (to be created from playbook tasks)

**Handler Files:**
handlers/main.yml (to be created from playbook handlers)

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

1. **main.yml** (`tasks/main.yml`):
   - Updates Apache SSL configuration to mitigate POODLE vulnerability
   - Legacy pattern: Uses short module name `replace` without FQCN
   - Modern equivalent: Use `ansible.builtin.replace` with proper FQCN
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Fix handler name consistency | poodle_fix.yml | Handler name in notify is "Restart apache2" but handler is defined as "Restart apache" |
| Playbook format | Role structure | poodle_fix.yml | Convert standalone playbook to proper role structure |
| Missing documentation | Add README.md | N/A | Document role purpose and variables |
| Missing meta | Add meta/main.yml | N/A | Add role metadata |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required for basic functionality

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the original playbook, but could add:
  - `ssl_config_path`: String, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
  - `ssl_protocol_setting`: String, default: "-all +TLSv1.2", description: "SSL protocol configuration string"

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
- Check SSL configuration file exists: `ls -la /etc/apache2/mods-available/ssl.conf`
- Validate Apache configuration after changes: `apache2ctl configtest`
- Test SSL configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify no SSLv3 support (POODLE mitigation): `openssl s_client -connect localhost:443 -ssl3` (should fail)