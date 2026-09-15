---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role structure. However, I can analyze it for modernization needs and provide a migration plan to convert it into a proper modern Ansible role.

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by updating Apache SSL configuration to disable vulnerable protocols and enable only TLSv1.2. The main modernization needs include converting from playbook to role structure, fixing FQCN usage, correcting handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration in Apache to disable all protocols except TLSv1.2
- Manages Apache2 and SSH service restarts
- Targets `/etc/apache2/mods-available/ssl.conf` configuration file

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
   - **Step 2**: Targets `/etc/apache2/mods-available/ssl.conf` file
   - **Step 3**: Replaces any existing `SSLProtocol` directive with `SSLProtocol -all +TLSv1.2`
   - **Legacy patterns found**: Non-FQCN module name, handler naming inconsistency
   - **Modern equivalent**: Use `ansible.builtin.replace` with proper error handling
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" vs "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |
| Missing defaults | Add defaults/main.yml | defaults/ | Configuration variables |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by the role)
**Services managed**: 
- apache2 (restarted after configuration change)
- sshd (restarted after configuration change)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable"
- `apache_service_name`: string, default: "apache2", description: "Name of Apache service"
- `restart_ssh`: boolean, default: true, description: "Whether to restart SSH service after SSL changes"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (argument validation)

**Services to check**: 
- apache2 service status and SSL configuration
- sshd service status

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
systemctl status apache2
apache2ctl -M | grep ssl

# Check current SSL configuration
grep SSLProtocol /etc/apache2/mods-available/ssl.conf

# Test SSL configuration after changes
apache2ctl configtest

# Verify services are running after restart
systemctl status apache2
systemctl status sshd

# Test SSL protocols (should only allow TLSv1.2)
nmap --script ssl-enum-ciphers -p 443 localhost
```

**Critical Issues Found:**
1. **Handler Naming Inconsistency**: The task notifies "Restart apache2" but the handler is named "Restart apache" - this will cause the handler to never execute
2. **Missing Error Handling**: No validation that the SSL configuration file exists before modification
3. **Hardcoded Paths**: Configuration file path is hardcoded, should be variable
4. **Missing Backup**: No backup of original configuration before modification
5. **No Validation**: No verification that the replacement was successful or that Apache can start with new configuration

**Recommended Enhancements for Modern Role:**
- Add backup of original configuration
- Add validation tasks to verify Apache configuration syntax
- Make file paths and service names configurable
- Add support for different Apache distributions (Ubuntu/CentOS/RHEL)
- Include pre-check to verify current SSL configuration
- Add post-check to validate SSL protocols are correctly configured