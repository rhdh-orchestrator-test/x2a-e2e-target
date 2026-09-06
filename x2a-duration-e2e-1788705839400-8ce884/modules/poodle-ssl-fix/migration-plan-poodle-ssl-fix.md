---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role structure. However, I can analyze it for modernization needs and provide a migration plan to convert it into a proper modern Ansible role. Let me provide the migration specification:

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by updating Apache SSL configuration to disable vulnerable protocols and enforce TLS 1.2. The main modernization needs include converting from playbook to role structure, fixing FQCN usage, correcting handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration in Apache to enforce TLS 1.2 only
- Manages Apache and SSH service restarts after configuration changes
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

1. **SSL Protocol Fix Task** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update Apache SSL configuration
   - **Step 2**: Legacy patterns found: missing FQCN, handler name mismatch
   - **Step 3**: Modern equivalent: `ansible.builtin.replace` with proper handler references
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (`poodle_fix.yml` handlers):
   - **Step 1**: Restarts Apache and SSH services after configuration changes
   - **Step 2**: Legacy patterns found: handler name inconsistency ("Restart apache" vs "Restart apache2" in notify)
   - **Step 3**: Modern equivalent: consistent handler naming and FQCN usage
   - Ansible module mapping: Already using `ansible.builtin.service` (modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache2" in both notify and handler |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |
| Hardcoded paths | Parameterized variables | tasks/main.yml | `/etc/apache2/mods-available/ssl.conf` |

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
- tasks/main.yml (converted task with FQCN)
- handlers/main.yml (consistent handler names)
- defaults/main.yml (parameterized variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (argument validation)

**Services to check**: 
- apache2 (should restart successfully)
- sshd (should restart successfully)

**Templates to validate**: 
None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
systemctl status apache2
apache2ctl -M | grep ssl

# Check current SSL configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify SSH service is running
systemctl status sshd

# Test Apache configuration syntax after changes
apache2ctl configtest

# Verify SSL protocol enforcement (post-change)
openssl s_client -connect localhost:443 -ssl3 2>&1 | grep "protocol version"
```

**Critical Migration Notes:**
1. **Handler Name Fix**: The notify references "Restart apache2" but the handler is named "Restart apache" - this must be corrected for idempotency
2. **Role Conversion**: Transform from playbook format to proper role structure with separate task and handler files
3. **Parameterization**: Make file paths and configuration strings configurable through variables
4. **Security Validation**: Add checks to ensure the SSL configuration change is applied correctly and doesn't break Apache startup
5. **Backup Strategy**: Consider adding a backup task before modifying the SSL configuration file