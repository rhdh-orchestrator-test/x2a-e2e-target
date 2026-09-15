---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, `chef-and-ansible/poodle_fix.yml` is not an Ansible role but rather a standalone playbook. However, I can analyze it for modernization and provide a migration plan to convert it into a proper modern Ansible role structure.

# Migration Plan: poodle_fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLSv1.2 protocol. It needs to be converted from a standalone playbook into a proper Ansible role structure with modern syntax and best practices.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Configures Apache SSL settings to disable vulnerable SSL protocols
- Enforces TLSv1.2 as the only allowed SSL/TLS protocol
- Restarts Apache and SSH services to apply changes
- Addresses POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability

## File Structure

**Current Structure** (Standalone Playbook):
```
poodle_fix.yml
```

**Target Role Structure** (To be created):
```
tasks/main.yml
handlers/main.yml
defaults/main.yml
meta/main.yml
meta/argument_specs.yml
```

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Configuration** (`poodle_fix.yml`):
   - Uses `replace` module to modify Apache SSL configuration
   - Replaces any existing SSLProtocol directive with secure TLSv1.2 only
   - Legacy patterns: Short module name, mixed handler naming
   - Modern equivalent: FQCN modules, consistent handler naming, proper role structure
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN required |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean modernization |
| Playbook structure | Role structure | All files | Convert to proper role |
| Mixed handler names | Consistent naming | handlers | "Restart apache" vs "Restart apache2" |
| Inline task parameters | Proper YAML structure | tasks | Multi-line parameter formatting |
| No argument validation | Argument specs | meta/ | Add role validation |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by the role)
**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

No templates present in the current playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `ssl_protocol`: string, default: "-all +TLSv1.2", description: "SSL protocol configuration for Apache"
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `apache_service_name`: string, default: "apache2", description: "Name of the Apache service"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted task)
- handlers/main.yml (standardized handlers)
- defaults/main.yml (configurable variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (input validation)

**Services to check**: 
- apache2 (should be running with TLSv1.2 only)
- sshd (should restart successfully)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl -t
sudo apache2ctl -S

# Check SSL protocol configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify TLS version with SSL test
openssl s_client -connect localhost:443 -tls1_2 -quiet

# Check service status
systemctl status apache2
systemctl status sshd

# Test POODLE vulnerability fix
nmap --script ssl-poodle localhost -p 443
```

## Additional Modernization Notes

**Critical Issues to Address:**
1. **Handler Name Mismatch**: The task notifies "Restart apache2" but the handler is named "Restart apache" - this will cause the handler to never execute
2. **Role Structure**: Convert from playbook to proper role structure with separate files
3. **Variable Parameterization**: Make paths and service names configurable
4. **Error Handling**: Add validation for Apache configuration before restart
5. **Idempotency**: The replace module is already idempotent, but add validation
6. **Platform Support**: Add support for different Apache distributions (httpd vs apache2)

**Security Considerations:**
- The role addresses a critical security vulnerability (POODLE)
- Should include validation that the configuration change was successful
- Consider adding support for additional secure protocols (TLSv1.3)
- Add checks to ensure Apache can start with the new configuration before applying

**Recommended Enhancements:**
- Add pre-task validation of Apache configuration syntax
- Include backup of original configuration
- Add support for multiple web servers (nginx, httpd)
- Include SSL certificate validation tasks
- Add monitoring/alerting for SSL configuration drift