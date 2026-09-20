---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role. However, I can analyze it for modernization needs and provide a migration plan to convert it into a proper modern Ansible role structure.

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2 protocol. The main modernization needs include converting from a playbook to a proper role structure, fixing FQCN usage, correcting handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Configures Apache to use only TLS 1.2 protocol
- Restarts Apache2 and SSH services after configuration changes
- Addresses POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability

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

1. **SSL Protocol Configuration** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, handler naming inconsistency
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper handler references
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers section):
   - **Step 1**: Restarts Apache2 and SSH services
   - **Step 2**: Legacy patterns found: Handler name mismatch ("Restart apache" vs "Restart apache2" in notify)
   - **Step 3**: Modern equivalent: Consistent handler naming and proper FQCN usage
   - Ansible module mapping: Already using `ansible.builtin.service` (correct)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" → "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Hardcoded paths | Variables | tasks/main.yml | `/etc/apache2/mods-available/ssl.conf` → variable |
| Hardcoded protocols | Variables | tasks/main.yml | `TLSv1.2` → configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2
- sshd

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"
- `restart_services`: list, default: ["apache2", "sshd"], description: "Services to restart after SSL configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (SSL configuration and restart)
- sshd (restart functionality)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
# Check current SSL configuration
grep SSLProtocol /etc/apache2/mods-available/ssl.conf
# Test Apache configuration syntax
apache2ctl configtest
# Verify services are running
systemctl status apache2
systemctl status sshd
# Test SSL configuration after applying role
openssl s_client -connect localhost:443 -tls1_2
```

**Critical Issues Found:**
1. **Handler Name Mismatch**: The task notifies "Restart apache2" but the handler is named "Restart apache" - this will cause the handler to never execute
2. **Playbook vs Role**: Current file is a playbook, not a role structure
3. **Hardcoded Values**: SSL configuration path and protocols are hardcoded
4. **Missing FQCN**: The `replace` module needs fully qualified collection name
5. **Boolean Syntax**: `become: yes` should be `become: true`

**Migration Priority**: HIGH - This addresses a critical security vulnerability (POODLE attack) and the handler naming issue could cause the fix to not take effect properly.