---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, `poodle_fix.yml` is a standalone Ansible playbook, not a role. However, I can still provide a migration plan to convert this playbook into a modern Ansible role structure and modernize its syntax. Let me analyze the content for modernization needs.

# Migration Plan: poodle_fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLSv1.2. The main modernization needs include converting from playbook to role structure, fixing handler naming inconsistency, adding proper file permissions, and implementing modern Ansible practices.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Configures Apache SSL settings to disable vulnerable SSL protocols
- Enforces TLSv1.2 only for SSL connections
- Restarts Apache and SSH services after configuration changes
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

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Configuration Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Replaces SSLProtocol directive to enforce TLSv1.2 only
   - **Step 3**: Notifies handlers to restart services
   - **Legacy patterns found**: 
     - Non-FQCN module name (`replace`)
     - Handler naming inconsistency (`Restart apache2` vs `Restart apache`)
     - Missing file permissions and backup options
     - Playbook structure instead of role
   - **Modern equivalent**: 
     - Use `ansible.builtin.replace` with proper error handling
     - Consistent handler naming
     - Add backup and validation options
     - Convert to role structure with proper variable management

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | `Restart apache2` → `Restart apache` |
| Hardcoded paths | Variables | tasks/main.yml, defaults/main.yml | `/etc/apache2/mods-available/ssl.conf` → variable |
| Missing backup | `backup: true` | tasks/main.yml | Add backup option |
| Missing validation | `validate:` parameter | tasks/main.yml | Add Apache config validation |
| Playbook structure | Role structure | All files | Convert to proper role |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.posix (for service management and file operations)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (restarted after SSL configuration)
- sshd (restarted as security measure)

## Template Modernization

No templates in current implementation. Consider adding:
- **ssl.conf.j2**: Template for Apache SSL configuration with variable SSL protocols

## Argument Specification

Variables for meta/argument_specs.yml:
- `apache_ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable in Apache"
- `apache_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `apache_service_name`: string, default: "apache2", description: "Name of Apache service"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after SSL changes"
- `backup_config`: boolean, default: true, description: "Whether to backup configuration files before modification"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (SSL configuration active)
- sshd (service running after restart)

**Templates to validate**: 
- Consider adding ssl.conf.j2 template for better configuration management

## Pre-flight checks:
```bash
# Verify Apache SSL configuration syntax
apache2ctl configtest

# Check SSL protocols are properly configured
openssl s_client -connect localhost:443 -tls1_2

# Verify services are running
systemctl status apache2
systemctl status sshd

# Test SSL configuration
nmap --script ssl-enum-ciphers -p 443 localhost
```

**Additional Security Considerations**:
- Add SSL cipher suite configuration
- Implement SSL certificate validation
- Add HSTS (HTTP Strict Transport Security) headers
- Consider adding fail2ban integration for additional security
- Add monitoring for SSL certificate expiration

**Role Conversion Notes**:
- The current playbook should be split into proper role structure
- Add proper error handling with `block`/`rescue`/`always`
- Implement idempotency checks
- Add tags for selective execution
- Consider adding molecule testing framework for role validation