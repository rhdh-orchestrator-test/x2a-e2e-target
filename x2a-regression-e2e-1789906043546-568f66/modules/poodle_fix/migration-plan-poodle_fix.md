---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook, not a role. However, the user has requested to analyze it for migration to a modern Ansible role. I'll create a migration plan to convert this playbook into a proper Ansible role with modern best practices.

# Migration Plan: poodle_fix

**TLDR**: This is currently a playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted into a proper Ansible role structure and modernized with current best practices including FQCN usage, proper file organization, and argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
- Manages Apache2 and SSH service restarts
- Targets `/etc/apache2/mods-available/ssl.conf` configuration file

## File Structure

**Current Structure** (Playbook):
```
poodle_fix.yml
```

**Target Role Structure**:
```
tasks/main.yml
handlers/main.yml
defaults/main.yml
meta/main.yml
meta/argument_specs.yml
```

**Task Files:**
tasks/main.yml

**Handler Files:**
handlers/main.yml

**Variable Files:**
defaults/main.yml

**Meta:**
meta/main.yml
meta/argument_specs.yml

**Templates:**
None

**Static Files:**
None

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix Task** (`poodle_fix.yml`):
   - Step 1: Uses `replace` module to modify Apache SSL configuration
   - Step 2: Legacy patterns found: non-FQCN module name, old-style parameter formatting
   - Step 3: Modern equivalent: Use `ansible.builtin.replace` with proper parameter structure
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Handler Management** (`poodle_fix.yml`):
   - Step 1: Defines service restart handlers for Apache and SSH
   - Step 2: Mixed handler naming (one uses FQCN, notification mismatch)
   - Step 3: Standardize all handlers with FQCN and fix notification names
   - Ansible module mapping: `service` → `ansible.builtin.service` (already partially modernized)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `dest=` parameter style | `path:` parameter | tasks/main.yml | Parameter modernization |
| Handler name mismatch | Fix notification targets | handlers/main.yml | "Restart apache2" vs "Restart apache" |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Hardcoded paths | Parameterized variables | tasks/main.yml | Make configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocols`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocols to configure"
- `apache_service_name`: string, default: "apache2", description: "Name of Apache service"
- `restart_ssh`: boolean, default: true, description: "Whether to restart SSH service after SSL changes"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 service status and configuration
- sshd service status

**Templates to validate**: 
None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
systemctl status apache2

# Verify SSH service is running
systemctl status sshd

# Check SSL configuration file exists
test -f /etc/apache2/mods-available/ssl.conf

# Validate SSL configuration syntax
apache2ctl configtest

# Test SSL protocols after changes
openssl s_client -connect localhost:443 -tls1_2 < /dev/null
```

**Key Migration Notes:**
1. **Critical Handler Fix**: The current playbook has a mismatch between the notification name "Restart apache2" and the handler name "Restart apache" - this must be corrected
2. **Security Focus**: This role specifically addresses the POODLE vulnerability (CVE-2014-3566) by disabling SSLv3 and older protocols
3. **Service Dependencies**: Both Apache and SSH services are restarted, which may indicate SSL configuration affects both services
4. **Parameterization**: The hardcoded paths and protocols should be made configurable through variables
5. **Idempotency**: The `replace` module is already idempotent, but should be tested to ensure proper behavior