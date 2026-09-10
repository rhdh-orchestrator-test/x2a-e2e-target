---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `chef-and-ansible/poodle_fix.yml` is not actually an Ansible role but rather a standalone playbook. However, I can still provide a migration plan to convert this playbook into a modern Ansible role structure. Let me analyze the content and create the migration specification.

# Migration Plan: poodle-security-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLSv1.2 protocol. The migration involves converting a standalone playbook into a proper Ansible role structure with modern syntax, FQCN usage, and proper error handling.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Configures Apache SSL settings to disable vulnerable SSL protocols
- Enforces TLSv1.2 as the only allowed SSL/TLS protocol
- Manages Apache and SSH service restarts after configuration changes
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

The role performs operations in this order:

1. **SSL Protocol Configuration** (`tasks/main.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: short module name, unquoted parameters, mixed handler naming
   - **Step 3**: Modern equivalent uses FQCN, proper quoting, consistent handler names
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (`handlers/main.yml`):
   - **Step 1**: Restarts Apache and SSH services after configuration changes
   - **Step 2**: Legacy patterns found: inconsistent handler naming, mixed FQCN usage
   - **Step 3**: Modern equivalent uses consistent naming and full FQCN
   - Ansible module mapping: Already uses `ansible.builtin.service` (partially modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `dest=` | `path:` | tasks/main.yml | Parameter name change |
| Unquoted parameters | Quoted YAML values | tasks/main.yml | YAML best practices |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Mixed handler names | Consistent naming | handlers/main.yml | Handler name consistency |
| Playbook structure | Role structure | All files | Convert to proper role |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.posix (for advanced file operations if needed)

**Role dependencies**: None
**External packages**: apache2 (managed by system package manager)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates present in the original playbook.

## Argument Specification

Variables for meta/argument_specs.yml:
- `apache_ssl_protocol`: string, default: "-all +TLSv1.2", description: "SSL protocol configuration for Apache"
- `apache_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `restart_services`: boolean, default: true, description: "Whether to restart services after configuration changes"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (should be running with TLSv1.2 only)
- sshd (should restart successfully)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest

# Check SSL protocol configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify Apache is running
systemctl status apache2

# Test SSL configuration (requires openssl)
echo | openssl s_client -connect localhost:443 -tls1_2 2>/dev/null | grep "Protocol"

# Verify SSH service status
systemctl status sshd
```

**Key Migration Notes**:
1. **Structure Conversion**: Transform standalone playbook into proper role structure
2. **Handler Consistency**: Fix handler name mismatch ("Restart apache" vs "Restart apache2")
3. **Parameter Modernization**: Update `dest=` to `path:` for replace module
4. **Variable Extraction**: Move hardcoded paths to configurable variables
5. **Error Handling**: Add validation for Apache configuration before restart
6. **Idempotency**: The replace module is already idempotent, but add validation
7. **Security Enhancement**: Consider adding SSL cipher suite configuration
8. **Platform Support**: Add support for different Apache distributions (httpd vs apache2)

**Critical Security Considerations**:
- Ensure the SSL protocol change doesn't break existing connections
- Validate that TLSv1.2 is supported on target systems
- Consider gradual rollout for production environments
- Add backup of original configuration before modification