---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role structure. However, I can analyze it for modernization needs and provide a migration plan to convert it into a proper modern Ansible role. Let me provide the detailed migration specification:

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLSv1.2 protocol. The main modernization needs include converting from a playbook to a proper role structure, fixing FQCN usage, correcting handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Modifies Apache SSL configuration to disable vulnerable protocols
- Enforces TLSv1.2 as the only allowed SSL/TLS protocol
- Manages Apache and SSH service restarts after configuration changes

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

1. **SSL Protocol Fix Task** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, inconsistent handler naming
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper FQCN
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (`poodle_fix.yml` handlers):
   - **Step 1**: Restarts Apache and SSH services after configuration changes
   - **Step 2**: Legacy patterns found: Handler name mismatch (`Restart apache` vs `Restart apache2` in notify)
   - **Step 3**: Modern equivalent: Consistent handler naming and proper FQCN usage
   - Ansible module mapping: Already uses `ansible.builtin.service` (correct)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | `Restart apache` → `Restart apache2` |
| Playbook structure | Role structure | All files | Convert to proper role |
| Hardcoded paths | Parameterized variables | tasks/main.yml | `/etc/apache2/mods-available/ssl.conf` → variable |
| Hardcoded protocols | Configurable protocols | tasks/main.yml | `TLSv1.2` → variable with secure defaults |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL/TLS protocols to enable"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration change"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (should be running and using TLSv1.2 only)
- sshd (should restart successfully)

**Templates to validate**: 
None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
# Test SSL configuration syntax
apache2ctl configtest
# Verify TLS protocol configuration
openssl s_client -connect localhost:443 -tls1_2
# Check that older protocols are disabled
openssl s_client -connect localhost:443 -ssl3 (should fail)
openssl s_client -connect localhost:443 -tls1 (should fail)
openssl s_client -connect localhost:443 -tls1_1 (should fail)
# Verify SSH service status
systemctl status sshd
```

**Critical Migration Notes:**
1. **Handler Name Inconsistency**: The original playbook has a critical bug where the task notifies `Restart apache2` but the handler is named `Restart apache`. This must be fixed during migration.
2. **Security Consideration**: The current configuration only allows TLSv1.2. Consider if TLSv1.3 should also be enabled for better security.
3. **Path Parameterization**: The hardcoded Apache configuration path should be made configurable to support different distributions (Debian/Ubuntu vs RHEL/CentOS).
4. **Idempotency**: The `replace` module is already idempotent, but consider adding validation to ensure the configuration change was successful.
5. **Error Handling**: Add proper error handling for cases where Apache configuration files don't exist or have different structures.