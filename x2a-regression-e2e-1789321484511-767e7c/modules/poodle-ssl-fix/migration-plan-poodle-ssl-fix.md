---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role. However, I can analyze it for modernization needs and provide a migration plan to convert it into a proper modern Ansible role structure.

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2 protocol. The main modernization needs include converting from a playbook to a proper role structure, fixing FQCN usage, correcting handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Configures Apache to use only TLS 1.2 protocol
- Restarts Apache and SSH services after configuration changes
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
   - **Step 2**: Legacy patterns found: non-FQCN module name, inconsistent handler naming
   - **Step 3**: Modern equivalent: Use FQCN `ansible.builtin.replace`, fix handler references
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers section):
   - **Step 1**: Restarts Apache and SSH services
   - **Step 2**: Legacy patterns found: Handler name mismatch ("Restart apache" vs "Restart apache2" in notify)
   - **Step 3**: Modern equivalent: Consistent handler naming, proper FQCN usage
   - Ansible module mapping: Already using `ansible.builtin.service` (correct)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" → "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Hardcoded paths | Parameterized variables | tasks/main.yml | `/etc/apache2/mods-available/ssl.conf` → variable |
| Hardcoded protocols | Configurable protocols | tasks/main.yml | `TLSv1.2` → variable with secure defaults |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL/TLS protocols to enable (Apache format)"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration change"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (should be running and using TLS 1.2 only)
- sshd (should be running normally)

**Templates to validate**: 
None

## Pre-flight checks:
```bash
# Verify Apache is installed and running
systemctl status apache2

# Check current SSL configuration
grep -i "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Test SSL configuration after role execution
openssl s_client -connect localhost:443 -tls1_2 -quiet

# Verify no weak protocols are accepted
openssl s_client -connect localhost:443 -ssl3 -quiet 2>&1 | grep -i "handshake failure"

# Check Apache configuration syntax
apache2ctl configtest

# Verify SSH service is still accessible
ssh -o ConnectTimeout=5 localhost "echo 'SSH working'"
```

**Critical Security Notes:**
- This role addresses CVE-2014-3566 (POODLE vulnerability)
- Disabling older SSL/TLS versions improves security but may break compatibility with very old clients
- Consider testing in non-production environment first
- The role currently restarts both Apache and SSH - the SSH restart may not be necessary for this specific fix

**Handler Naming Issue:**
The current playbook has a critical bug where the task notifies "Restart apache2" but the handler is named "Restart apache". This will cause the handler to never execute, leaving Apache with the old configuration until manually restarted.