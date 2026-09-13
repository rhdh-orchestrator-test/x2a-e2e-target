---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a standalone playbook, not a role structure. However, I can still provide a migration plan to modernize this into a proper Ansible role following current best practices.

# Migration Plan: poodle_fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2. The main modernization needs include converting from a standalone playbook to a proper role structure, updating handler naming consistency, adding proper argument specifications, and implementing modern Ansible best practices.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Configures SSL protocol to use only TLS 1.2 by modifying `/etc/apache2/mods-available/ssl.conf`
- Restarts Apache2 and SSH services to apply changes
- Targets systems with Apache2 web server installed

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

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Configuration Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, inconsistent handler naming
   - **Step 3**: Modern equivalent: Use FQCN `ansible.builtin.replace`, consistent handler naming
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Restart Handlers**:
   - **Handler inconsistency**: Notifies "Restart apache2" but handler is named "Restart apache"
   - **Modern approach**: Consistent naming and proper FQCN usage

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache2" → "restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role |
| No argument specs | Add meta/argument_specs.yml | meta/ | Role validation |
| Hardcoded paths | Parameterized variables | defaults/main.yml | Flexibility |

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
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration change"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (argument validation)

**Services to check**: 
- apache2 (should be running and using TLS 1.2 only)
- sshd (should be running after restart)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
# Check current SSL configuration
grep SSLProtocol /etc/apache2/mods-available/ssl.conf
# Verify Apache configuration syntax
apache2ctl configtest
# Check Apache service status
systemctl status apache2
# Verify SSH service status
systemctl status sshd
# Test SSL configuration (post-migration)
openssl s_client -connect localhost:443 -tls1_2
```

**Key Migration Notes:**
1. **Handler Naming Issue**: The current playbook has a critical bug - it notifies "Restart apache2" but the handler is named "Restart apache". This needs to be fixed during migration.
2. **Role Structure**: Convert from standalone playbook to proper role structure with separate tasks, handlers, defaults, and meta directories.
3. **Parameterization**: Make file paths and configuration values configurable through variables.
4. **Error Handling**: Add proper error handling and validation for the SSL configuration changes.
5. **Idempotency**: The `replace` module is already idempotent, but consider adding validation tasks to verify the configuration was applied correctly.