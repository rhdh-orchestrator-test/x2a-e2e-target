---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role structure. However, I can analyze it for modernization needs and provide a migration plan to convert it into a proper modern Ansible role. Let me provide the migration specification:

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by updating Apache SSL configuration to disable vulnerable protocols and enable only TLS 1.2. The main modernization needs include converting from a playbook to a proper role structure, fixing FQCN usage, correcting handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration in Apache to disable all protocols except TLS 1.2
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

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, handler naming inconsistency
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper FQCN
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers):
   - **Step 1**: Restarts Apache2 and SSH services after configuration changes
   - **Step 2**: Legacy patterns found: Handler name mismatch (`Restart apache2` vs `Restart apache`)
   - **Step 3**: Modern equivalent: Fix handler naming consistency and use FQCN
   - Ansible module mapping: `service` → `ansible.builtin.service` (already correct in handlers)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Fix naming consistency | handlers/main.yml | `Restart apache2` → `Restart apache` |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |
| Hardcoded paths | Parameterize configuration | defaults/main.yml | Make configurable |

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
- tasks/main.yml (converted from playbook)
- handlers/main.yml (extracted from playbook)
- defaults/main.yml (new file with variables)
- meta/main.yml (new role metadata)
- meta/argument_specs.yml (new argument specifications)

**Services to check**: 
- apache2 service status and configuration
- sshd service status

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

# Verify SSH service status  
sudo systemctl status sshd

# Test SSL configuration with openssl
echo | openssl s_client -connect localhost:443 -tls1_2 2>/dev/null | grep "Protocol"
```

**Critical Migration Notes:**
1. **Handler Naming Fix**: The playbook has a mismatch where the task notifies `Restart apache2` but the handler is named `Restart apache`. This must be corrected.
2. **Playbook to Role Conversion**: This is currently a playbook targeting a specific host. It needs to be converted to a reusable role structure.
3. **Parameterization**: Hardcoded paths and configuration values should be moved to defaults/main.yml for flexibility.
4. **FQCN Compliance**: The `replace` module needs to be updated to `ansible.builtin.replace`.
5. **Boolean Modernization**: `become: yes` should be `become: true`.
6. **Security Consideration**: The role should validate that Apache is installed before attempting configuration changes.