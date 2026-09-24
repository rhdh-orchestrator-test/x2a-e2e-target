---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role structure. However, I can provide a migration plan to convert this into a modern Ansible role. Let me provide the detailed migration specification:

# Migration Plan: poodle-fix-example

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by updating Apache SSL configuration to disable vulnerable protocols and enforce TLSv1.2. The main modernization needs include converting from a playbook to a proper role structure, fixing FQCN usage, correcting handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration in `/etc/apache2/mods-available/ssl.conf`
- Disables all SSL protocols and enables only TLSv1.2
- Restarts Apache2 and SSH services after configuration changes
- Provides security hardening for web servers against SSL/TLS vulnerabilities

## File Structure

**Current Structure (Playbook):**
```
poodle_fix.yml
```

**Target Role Structure:**
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

1. **SSL Configuration Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update Apache SSL configuration
   - **Step 2**: Legacy patterns found: missing FQCN, inconsistent handler naming
   - **Step 3**: Modern equivalent: use `ansible.builtin.replace` with proper FQCN
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers section):
   - **Step 1**: Restarts Apache2 and SSH services
   - **Step 2**: Legacy patterns: handler name mismatch ("Restart apache" vs "Restart apache2")
   - **Step 3**: Modern equivalent: consistent handler naming and proper FQCN usage

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" → "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |
| Hardcoded paths | Parameterized variables | tasks/main.yml | Make configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by system, not installed by role)
**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_services`: list, default: ["apache2", "sshd"], description: "List of services to restart after SSL configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted from playbook tasks)
- handlers/main.yml (extracted handlers with corrected names)
- defaults/main.yml (new file with configurable variables)
- meta/main.yml (new role metadata)
- meta/argument_specs.yml (new argument specifications)

**Services to check**: 
- apache2 (should restart successfully)
- sshd (should restart successfully)

**Templates to validate**: 
None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration syntax
apache2ctl configtest

# Check SSL protocol configuration
openssl s_client -connect localhost:443 -tls1_2

# Verify services are running after restart
systemctl status apache2
systemctl status sshd

# Test SSL configuration with SSL Labs or similar tool
# Verify POODLE vulnerability is fixed
```

**Critical Migration Notes:**
1. **Handler Name Fix**: The notify calls "Restart apache2" but handler is named "Restart apache" - this must be corrected
2. **Role Structure**: Convert from playbook format to proper role structure
3. **Parameterization**: Make file paths and SSL configuration configurable through variables
4. **FQCN**: Add fully qualified collection names for all modules
5. **Boolean Values**: Convert `yes` to `true` for become directive
6. **Error Handling**: Consider adding validation to ensure Apache configuration is valid before restart
7. **Idempotency**: The replace module is already idempotent, but consider adding validation tasks