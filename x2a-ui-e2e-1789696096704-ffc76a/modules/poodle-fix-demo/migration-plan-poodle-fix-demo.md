---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a traditional Ansible role structure. However, I can still provide a migration plan to modernize this into a proper Ansible role following current best practices.

# Migration Plan: poodle-fix-demo

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by updating Apache SSL configuration to disable vulnerable protocols and enforce TLS 1.2. The main modernization needs include converting from a playbook to a proper role structure, fixing handler naming inconsistencies, and applying FQCN standards.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration in `/etc/apache2/mods-available/ssl.conf`
- Disables all SSL protocols and enables only TLS 1.2
- Restarts Apache2 and SSH services after configuration changes

## File Structure

**Current Structure (Playbook):**
```
poodle_fix.yml
```

**Target Role Structure:**
```
tasks/main.yml
handlers/main.yml
meta/main.yml
meta/argument_specs.yml
defaults/main.yml
README.md
```

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Configuration Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update Apache SSL configuration
   - **Step 2**: Targets `/etc/apache2/mods-available/ssl.conf` file
   - **Step 3**: Replaces any existing `SSLProtocol` directive with `SSLProtocol -all +TLSv1.2`
   - **Legacy patterns found**: Non-FQCN module name, handler naming inconsistency
   - **Modern equivalent**: Use `ansible.builtin.replace` with proper handler references
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent handler naming | handlers/main.yml | "Restart apache" vs "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: Apache2 web server (assumed pre-installed)
**Services managed**: 
- apache2 (restarted after SSL config change)
- sshd (restarted after SSL config change)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_services`: list, default: ["apache2", "sshd"], description: "Services to restart after SSL configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted task with FQCN)
- handlers/main.yml (consistent handler names)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)
- defaults/main.yml (default variables)

**Services to check**: 
- apache2 (SSL configuration applied and service restarted)
- sshd (service restarted successfully)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
# Check current SSL configuration
grep SSLProtocol /etc/apache2/mods-available/ssl.conf
# Test Apache configuration syntax
apache2ctl configtest
# Verify services are running
systemctl status apache2
systemctl status sshd
# Test SSL configuration after applying changes
openssl s_client -connect localhost:443 -tls1_2
```

**Key Migration Notes:**
1. **Handler Inconsistency**: The notify references "Restart apache2" but the handler is named "Restart apache" - this needs to be fixed for idempotency
2. **Security Focus**: This role specifically addresses the POODLE vulnerability (CVE-2014-3566) by disabling SSL 3.0
3. **Service Dependencies**: Both Apache and SSH are restarted, suggesting this might be part of a broader security hardening effort
4. **File Path Assumption**: The role assumes Debian/Ubuntu Apache structure (`/etc/apache2/`) - should be made configurable for cross-platform support