---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a traditional Ansible role structure. However, I can still provide a migration plan to modernize this into a proper Ansible role following current best practices.

# Migration Plan: poodle-fix-demo

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLSv1.2 protocol. The migration involves converting a standalone playbook into a proper Ansible role structure with modern syntax, FQCN usage, and proper error handling.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Configures Apache SSL settings to disable vulnerable SSL protocols
- Enforces TLSv1.2 as the only allowed SSL/TLS protocol
- Manages Apache2 and SSH service restarts
- Addresses POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability

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

1. **SSL Protocol Configuration** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, hardcoded paths, `become: yes` syntax
   - **Step 3**: Modern equivalent: FQCN `ansible.builtin.replace`, parameterized paths, `become: true`
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers):
   - **Step 1**: Restarts Apache2 and SSH services after configuration changes
   - **Step 2**: Legacy patterns: Handler name mismatch (notifies "Restart apache2" but handler named "Restart apache")
   - **Step 3**: Modern equivalent: Consistent handler naming, proper FQCN usage
   - Ansible module mapping: Already uses `ansible.builtin.service` (partially modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `become: yes` | `become: true` | poodle_fix.yml | Boolean modernization |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent naming | poodle_fix.yml | "Restart apache2" → "Restart apache" |
| Hardcoded paths | Parameterized variables | poodle_fix.yml | `/etc/apache2/mods-available/ssl.conf` → variable |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| Missing `mode:` | Add file permissions | tasks/main.yml | File modification security |
| No error handling | Add `block`/`rescue` | tasks/main.yml | Proper error handling |

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
- `apache_service_name`: string, default: "apache2", description: "Name of the Apache service"
- `ssh_service_name`: string, default: "sshd", description: "Name of the SSH service"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (SSL configuration applied)
- sshd (service restart capability)

**Templates to validate**: 
None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest

# Check SSL protocol configuration
sudo grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify Apache service status
sudo systemctl status apache2

# Test SSL configuration with openssl
echo | openssl s_client -connect localhost:443 -tls1_2 2>/dev/null | grep "Protocol"

# Verify SSH service status
sudo systemctl status sshd

# Check Apache error logs for SSL-related issues
sudo tail -f /var/log/apache2/error.log
```

**Critical Migration Notes:**
1. **Handler Name Consistency**: The current playbook has a mismatch where it notifies "Restart apache2" but the handler is named "Restart apache". This must be fixed.
2. **Security Enhancement**: Add file backup and validation steps before modifying SSL configuration.
3. **Idempotency**: The `replace` module is already idempotent, but consider adding validation tasks.
4. **Error Handling**: Wrap the SSL configuration change in a block/rescue structure to handle potential Apache configuration errors.
5. **Variable Parameterization**: Convert hardcoded paths and values to variables for better reusability across different distributions.