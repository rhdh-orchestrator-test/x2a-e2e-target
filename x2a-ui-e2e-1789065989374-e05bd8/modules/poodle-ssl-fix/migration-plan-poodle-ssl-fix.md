---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a standalone Ansible playbook, not a role. However, the user is asking to analyze it for migration to a modern Ansible role. I'll create a migration plan that converts this playbook into a proper Ansible role structure with modern best practices.

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a standalone playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook to a proper Ansible role structure and modernized with current best practices including FQCN usage, proper variable management, and role structure.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
- Manages Apache2 and SSH service restarts
- Targets Apache SSL module configuration

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
None required

**Static Files:**
None required

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, playbook structure instead of role
   - **Step 3**: Modern equivalent: Convert to role structure with `ansible.builtin.replace`
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers):
   - **Step 1**: Restarts Apache2 and SSH services after configuration changes
   - **Step 2**: Legacy patterns found: Handler name mismatch (notifies "Restart apache2" but handler named "Restart apache")
   - **Step 3**: Modern equivalent: Fix handler name consistency, use FQCN
   - Ansible module mapping: `service` → `ansible.builtin.service` (already modernized in handlers)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| Playbook structure | Role structure | All files | Convert to proper role |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | Fix "apache2" vs "apache" |
| Hardcoded paths | Variables | tasks/main.yml | Make paths configurable |
| Hardcoded protocols | Variables | tasks/main.yml | Make SSL protocols configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates are used in this role.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default "/etc/apache2/mods-available/ssl.conf", Apache SSL configuration file path
- `ssl_protocols`: string, default "-all +TLSv1.2", SSL protocols to enable
- `restart_apache`: boolean, default true, Whether to restart Apache after changes
- `restart_sshd`: boolean, default true, Whether to restart SSH after changes

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (should be running with updated SSL config)
- sshd (should be running normally)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest

# Check SSL protocols are properly configured
sudo grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify Apache is running
sudo systemctl status apache2

# Verify SSH is running  
sudo systemctl status sshd

# Test SSL configuration (if Apache is serving HTTPS)
openssl s_client -connect localhost:443 -tls1_2 < /dev/null

# Verify POODLE vulnerability is fixed
nmap --script ssl-poodle localhost -p 443
```

**Critical Issues Found:**
1. **Handler Name Mismatch**: The task notifies "Restart apache2" but the handler is named "Restart apache"
2. **Playbook vs Role**: Current structure is a playbook, needs conversion to role
3. **Hardcoded Values**: SSL configuration path and protocols should be variables
4. **Missing FQCN**: The `replace` module needs fully qualified collection name
5. **Boolean Syntax**: `become: yes` should be `become: true`

**Migration Priority**: High - This addresses a critical security vulnerability (POODLE) and should be properly structured as a reusable role.