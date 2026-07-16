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
tasks/main.yml

**Handler Files:**
handlers/main.yml

**Variable Files:**
defaults/main.yml

**Meta:**
meta/main.yml

**Templates:**
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Legacy pattern: Uses short module name `replace` without FQCN
   - Modern equivalent: Use `ansible.builtin.replace` with proper parameter formatting
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch between task notification and handler definition
   - Modern equivalent: Ensure handler names match exactly between notifications and definitions
   - Ansible module mapping: Already using FQCN `ansible.builtin.service`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Handler name mismatch | Match handler names exactly | tasks/main.yml, handlers/main.yml | "Restart apache2" notification vs "Restart apache" handler |
| Playbook format | Role structure | All files | Convert standalone playbook to proper role structure |
| `become: yes` | `become: true` | tasks/main.yml | Boolean syntax |

## Dependencies

**Collection dependencies** (for requirements.yml):
- No external collections required, only ansible.builtin modules are used

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables are defined in the original playbook, but could add:
  - `ssl_config_path`: String, default: '/etc/apache2/mods-available/ssl.conf', Path to Apache SSL configuration
  - `ssl_protocol_setting`: String, default: '-all +TLSv1.2', SSL protocol configuration string

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
- Check SSL configuration file exists: `ls -la /etc/apache2/mods-available/ssl.conf`
- Validate Apache configuration after changes: `apache2ctl configtest`
- Test SSL configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify POODLE vulnerability is mitigated: `nmap --script ssl-enum-ciphers -p 443 localhost`