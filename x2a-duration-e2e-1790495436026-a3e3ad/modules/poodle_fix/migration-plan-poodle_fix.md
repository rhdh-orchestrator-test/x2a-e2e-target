---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, `poodle_fix.yml` is a standalone Ansible playbook, not a role. However, I can still provide a migration plan to convert this playbook into a modern Ansible role structure and modernize its syntax. Let me analyze the content for modernization needs.

# Migration Plan: poodle_fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2. The main modernization needs include converting from playbook to role structure, fixing handler naming inconsistency, adding proper file permissions, and implementing modern Ansible practices.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Configures Apache SSL settings to disable vulnerable SSL protocols
- Enforces TLS 1.2 only for Apache web server
- Manages Apache and SSH service restarts
- Addresses POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability

## File Structure

**Current Structure (Playbook):**
```
poodle_fix.yml
```

**Target Structure (Role):**
```
tasks/main.yml
handlers/main.yml
defaults/main.yml
meta/main.yml
meta/argument_specs.yml
```

## Module Explanation

The playbook performs operations in this order:

1. **SSL Configuration Task** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, missing file permissions, handler name mismatch
   - **Step 3**: Modern equivalent: Use FQCN `ansible.builtin.replace`, add `mode` parameter, fix handler names
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Handler Issues** (`poodle_fix.yml`):
   - **Critical Issue**: Task notifies "Restart apache2" but handler is named "Restart apache"
   - **Step 1**: Handler name mismatch will cause task failure
   - **Step 2**: Both handlers already use modern FQCN syntax
   - **Step 3**: Fix handler name consistency

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| Missing `mode:` | Add `mode: '0644'` | tasks/main.yml | File permissions best practice |
| Handler name mismatch | Fix "Restart apache2" → "Restart apache" | handlers/main.yml | Critical bug fix |
| Playbook structure | Role structure | All files | Convert to proper role |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Hard-coded paths | Variables | tasks/main.yml | Parameterization |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed pre-installed)
**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

No templates present in the original playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default "/etc/apache2/mods-available/ssl.conf", description "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default "SSLProtocol -all +TLSv1.2", description "SSL protocol configuration string"
- `apache_service_name`: string, default "apache2", description "Name of Apache service"
- `ssh_service_name`: string, default "sshd", description "Name of SSH service"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted task)
- handlers/main.yml (fixed handler names)
- defaults/main.yml (parameterized variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (input validation)

**Services to check**: 
- apache2 service status and configuration
- sshd service status

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest

# Check SSL protocol settings
sudo grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify services are running
sudo systemctl status apache2
sudo systemctl status sshd

# Test SSL configuration (if applicable)
openssl s_client -connect localhost:443 -tls1_2
```

**Critical Issues Found:**
1. **Handler Name Mismatch**: Task notifies "Restart apache2" but handler is named "Restart apache" - this will cause the playbook to fail
2. **Missing File Permissions**: The `replace` task should include `mode: '0644'` for security best practices
3. **Playbook vs Role Structure**: Current file is a playbook, needs conversion to proper role structure
4. **Hard-coded Paths**: Configuration file path should be parameterized for flexibility across different distributions

**Migration Priority**: High - This addresses a critical security vulnerability (POODLE) and has a handler bug that prevents proper execution.