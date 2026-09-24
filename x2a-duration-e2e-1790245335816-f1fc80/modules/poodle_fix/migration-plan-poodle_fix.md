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

**Target Modern Role Structure**:
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

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN required |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean modernization |
| Playbook structure | Role structure | All files | Convert to proper role |
| Mixed handler names | Consistent naming | handlers | "Restart apache" vs "Restart apache2" |
| Inline parameters | Structured parameters | tasks | Multi-line parameter formatting |
| No argument specs | Add argument_specs.yml | meta/ | Role validation |
| No defaults | Add defaults/main.yml | defaults/ | Configurable variables |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core modules)

**Role dependencies**: None
**External packages**: apache2 (managed by system, not installed by role)
**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

No templates present in the current playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_protocol`: string, default: "-all +TLSv1.2", description: "SSL protocol configuration for Apache"
- `apache_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `restart_services`: boolean, default: true, description: "Whether to restart services after configuration changes"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted task with FQCN)
- handlers/main.yml (consistent handler names)
- defaults/main.yml (configurable variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (input validation)

**Services to check**: 
- apache2 service status and SSL configuration
- sshd service status

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
systemctl status apache2
apache2ctl -M | grep ssl

# Test SSL configuration syntax
apache2ctl configtest

# Verify SSH service is running
systemctl status sshd

# Test SSL protocol after changes
openssl s_client -connect localhost:443 -tls1_2

# Verify POODLE vulnerability is fixed
nmap --script ssl-poodle localhost -p 443
```

**Key Migration Notes**:
1. The original is a playbook, not a role - complete restructuring needed
2. Handler naming inconsistency needs resolution ("Restart apache" vs "Restart apache2")
3. Hard-coded paths should be made configurable via variables
4. Add proper error handling and validation
5. Consider adding checks for Apache SSL module availability
6. Add support for different Linux distributions (currently Ubuntu/Debian specific)