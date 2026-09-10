---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a standalone playbook file, not a traditional Ansible role with the standard directory structure (tasks/, handlers/, defaults/, etc.). However, I can still provide a migration plan to modernize this into a proper Ansible role following current best practices.

# Migration Plan: poodle_fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2. The main modernization needs include converting from a standalone playbook to a proper role structure, fixing handler naming inconsistencies, adding proper argument specifications, and implementing modern Ansible practices.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Configures Apache SSL settings to disable vulnerable SSL protocols
- Enforces TLS 1.2 only protocol in Apache configuration
- Manages Apache and SSH service restarts after configuration changes
- Targets POODLE vulnerability mitigation (CVE-2014-3566)

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

The playbook performs operations in this order:

1. **SSL Configuration Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, inconsistent handler naming
   - **Step 3**: Modern equivalent: `ansible.builtin.replace` with proper handler references
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers section):
   - **Step 1**: Restarts Apache and SSH services after configuration changes
   - **Step 2**: Legacy patterns found: handler name mismatch (`Restart apache2` vs `Restart apache`)
   - **Step 3**: Modern equivalent: consistent handler naming and FQCN usage
   - Ansible module mapping: `service` → `ansible.builtin.service` (already modernized in handlers)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | `Restart apache2` → `Restart apache` |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |
| Hardcoded paths | Parameterized variables | defaults/main.yml | Configuration flexibility |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by system, not installed by role)
**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration change"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (argument validation)

**Services to check**: 
- apache2 (should be running and configured with TLS 1.2 only)
- sshd (should be running after restart)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl -t
sudo apache2ctl -S

# Check SSL protocol configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify services are running
systemctl status apache2
systemctl status sshd

# Test SSL configuration (requires external testing)
nmap --script ssl-enum-ciphers -p 443 localhost
```

**Additional Migration Notes:**

1. **Handler Naming Issue**: The current playbook has a critical bug where the task notifies `Restart apache2` but the handler is named `Restart apache`. This will cause the handler to never execute.

2. **Security Considerations**: The role should be expanded to include:
   - SSL cipher suite configuration
   - HTTP Strict Transport Security (HSTS) headers
   - SSL certificate validation

3. **Platform Compatibility**: The current implementation assumes Debian/Ubuntu (apache2). Consider adding support for RHEL/CentOS (httpd).

4. **Idempotency**: The `replace` module is already idempotent, which is good.

5. **Error Handling**: Consider adding validation to ensure Apache configuration is valid before restarting services.