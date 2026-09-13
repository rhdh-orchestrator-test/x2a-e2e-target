---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a traditional Ansible role structure. However, I can still provide a migration plan to modernize this into a proper Ansible role following current best practices.

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLSv1.2 protocol. The main modernization needs include converting from a playbook to a proper role structure, fixing FQCN usage, correcting handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Configures Apache SSL settings to disable vulnerable SSL protocols
- Replaces SSLProtocol directive in Apache configuration to use only TLSv1.2
- Restarts Apache2 and SSH services after configuration changes
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

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Configuration** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: missing FQCN, handler naming inconsistency
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper error handling
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers section):
   - **Step 1**: Restarts Apache2 and SSH services
   - **Step 2**: Legacy patterns found: Handler name mismatch ("Restart apache" vs "Restart apache2")
   - **Step 3**: Modern equivalent: Consistent handler naming and FQCN usage
   - Ansible module mapping: Already using `ansible.builtin.service` (correct)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" → "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |
| Hard-coded paths | Parameterized variables | tasks/main.yml | Make configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (must be pre-installed)
**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_services`: list, default: ["apache2", "sshd"], description: "List of services to restart after SSL configuration"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (argument validation)

**Services to check**: 
- apache2 (SSL configuration applied and service running)
- sshd (service running after restart)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
# Check current SSL configuration
grep -n "SSLProtocol" /etc/apache2/mods-available/ssl.conf
# Test Apache configuration syntax
apache2ctl configtest
# Verify services are running
systemctl status apache2
systemctl status sshd
# Test SSL configuration with openssl
echo | openssl s_client -connect localhost:443 -tls1_2 2>/dev/null | grep "Protocol"
```

**Critical Migration Notes**:
1. **Handler Naming Bug**: The current playbook has a critical bug where it notifies "Restart apache2" but the handler is named "Restart apache" - this must be fixed during migration
2. **Security Impact**: This role addresses a critical security vulnerability (POODLE), so testing should include SSL/TLS protocol verification
3. **Service Dependencies**: Both Apache and SSH restarts are included, which suggests this might be part of a broader security hardening effort
4. **Configuration Backup**: Consider adding a backup task before modifying SSL configuration for rollback capability