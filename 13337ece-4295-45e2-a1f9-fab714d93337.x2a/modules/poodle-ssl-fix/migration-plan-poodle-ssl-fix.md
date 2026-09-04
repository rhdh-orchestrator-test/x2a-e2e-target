---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a traditional Ansible role structure. However, I can provide a migration plan to convert this into a modern Ansible role. Let me provide the detailed migration specification:

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2 protocol. The main modernization needs include converting from a playbook to a proper role structure, using FQCN for modules, fixing handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Configures Apache SSL settings to disable vulnerable SSL protocols
- Replaces SSLProtocol configuration to use only TLS 1.2
- Manages Apache2 and SSH service restarts
- Addresses POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability

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
None

**Static Files:**
None

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Configuration** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: short module name, inconsistent handler naming
   - **Step 3**: Modern equivalent: FQCN module name, consistent handler references
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" vs "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Inline parameters | Structured parameters | tasks/main.yml | Multi-line parameter formatting |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by system)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
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
- apache2 service status and configuration
- sshd service status

**Templates to validate**: 
None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
# Check current SSL configuration
grep SSLProtocol /etc/apache2/mods-available/ssl.conf
# Verify Apache configuration syntax
apache2ctl configtest
# Check service status
systemctl status apache2
systemctl status sshd
# Test SSL configuration after changes
openssl s_client -connect localhost:443 -tls1_2
```

**Key Migration Notes:**
1. **Handler Naming Issue**: The current playbook has a mismatch between the notify target ("Restart apache2") and the actual handler name ("Restart apache"). This needs to be corrected.
2. **Role Structure**: Convert from a single playbook file to a proper role structure with separate task and handler files.
3. **Variable Parameterization**: Make the SSL protocol configuration and file paths configurable through variables.
4. **Error Handling**: Add proper error handling and validation for the configuration changes.
5. **Idempotency**: The `replace` module is already idempotent, but consider adding validation tasks.