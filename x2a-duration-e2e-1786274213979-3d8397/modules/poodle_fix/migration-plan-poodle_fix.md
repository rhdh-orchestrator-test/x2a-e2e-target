---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper handler naming, and structured organization into a proper Ansible role format.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate the POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a properly structured Ansible role. The migration will involve converting this playbook into a proper role structure.**

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

1. **Main Tasks** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Legacy pattern: Short module name `replace:` without FQCN
   - Modern equivalent: `ansible.builtin.replace:`
   - Notifies handlers to restart services after configuration changes

2. **Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Uses the `ansible.builtin.service` module (already using FQCN)
   - Handler name mismatch: Notification uses "Restart apache2" but handler is named "Restart apache"

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent handler naming | poodle_fix.yml | Handler "Restart apache" should match notification "Restart apache2" |
| Standalone playbook | Proper role structure | poodle_fix.yml | Convert to role with tasks/main.yml, handlers/main.yml, etc. |
| No argument specifications | Add meta/argument_specs.yml | N/A | Define role parameters |
| No role metadata | Add meta/main.yml | N/A | Define role metadata |

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
- `apache_ssl_config_path`: 
  - type: str
  - default: "/etc/apache2/mods-available/ssl.conf"
  - description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: 
  - type: str
  - default: "-all +TLSv1.2"
  - description: "SSL protocol configuration string for Apache"

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
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Check SSL configuration syntax: `apache2ctl configtest`
- Verify SSL protocols after applying: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Test HTTPS connectivity after applying: `curl -k https://localhost`