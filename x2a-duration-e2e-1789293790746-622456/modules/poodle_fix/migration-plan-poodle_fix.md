---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, `chef-and-ansible/poodle_fix.yml` is not an Ansible role but rather a standalone playbook. However, I can create a migration plan to convert this playbook into a modern Ansible role structure. Let me analyze the content and create the migration specification.

# Migration Plan: poodle_fix

**TLDR**: This is currently a standalone playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook to a proper Ansible role structure and modernized with current best practices including FQCN usage, proper handler naming consistency, and role-based organization.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
- Manages Apache2 and SSH service restarts
- Targets SSL configuration in `/etc/apache2/mods-available/ssl.conf`

## File Structure

**Current Structure (Playbook):**
```
poodle_fix.yml
```

**Target Role Structure:**
```
tasks/main.yml
handlers/main.yml
meta/main.yml
defaults/main.yml
meta/argument_specs.yml
```

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, inconsistent handler naming
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper FQCN
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers section):
   - **Step 1**: Restarts Apache2 and SSH services after configuration changes
   - **Step 2**: Legacy patterns: Handler name mismatch (`Restart apache` vs `Restart apache2` in notify)
   - **Step 3**: Modern equivalent: Consistent handler naming and FQCN usage
   - Ansible module mapping: Already using `ansible.builtin.service` (modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | `Restart apache` → `Restart apache2` |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| Inline task parameters | Proper YAML structure | tasks/main.yml | Multi-line parameter formatting |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates present in the current playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
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
- apache2 (should restart successfully)
- sshd (should restart successfully)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest

# Check SSL protocol configuration
sudo grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify services are running
sudo systemctl status apache2
sudo systemctl status sshd

# Test SSL configuration (if applicable)
openssl s_client -connect localhost:443 -tls1_2

# Verify POODLE vulnerability is fixed
nmap --script ssl-poodle localhost -p 443
```

**Critical Migration Notes**:
1. **Handler Name Consistency**: The current playbook has a mismatch where the task notifies `Restart apache2` but the handler is named `Restart apache`. This must be fixed for idempotency.
2. **Role Structure**: Convert from playbook to proper role structure with separate task and handler files.
3. **Variable Parameterization**: Hard-coded paths and service names should be moved to defaults/main.yml for flexibility.
4. **Security Validation**: Add tasks to validate the SSL configuration change was successful.
5. **Platform Compatibility**: Consider adding support for different Apache distributions (httpd vs apache2).