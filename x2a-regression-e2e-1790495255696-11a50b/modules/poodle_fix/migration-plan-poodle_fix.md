---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `chef-and-ansible/poodle_fix.yml` is not actually an Ansible role, but rather a standalone playbook. However, I can still provide a migration plan to convert this playbook into a modern Ansible role structure and modernize its content.

# Migration Plan: poodle_fix

**TLDR**: This is currently a standalone playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook to a proper role structure and modernized with current Ansible best practices including FQCN usage, proper handler naming consistency, and role organization.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
- Manages Apache2 and SSH service restarts
- Targets SSL configuration in `/etc/apache2/mods-available/ssl.conf`

## File Structure

**Current Structure** (Playbook):
```
poodle_fix.yml
```

**Target Role Structure** (Post-Migration):
```
tasks/main.yml
handlers/main.yml
meta/main.yml
defaults/main.yml
meta/argument_specs.yml
```

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix Task** (`poodle_fix.yml`):
   - Uses `replace` module to update Apache SSL configuration
   - Replaces any existing `SSLProtocol` directive with secure TLSv1.2 only
   - Targets `/etc/apache2/mods-available/ssl.conf` file
   - Notifies both Apache and SSH restart handlers
   - Legacy patterns: Missing FQCN, inconsistent handler naming
   - Modern equivalent: Use `ansible.builtin.replace` with consistent handler names

2. **Handler Section** (`poodle_fix.yml`):
   - Contains two service restart handlers
   - Handler naming inconsistency: "Restart apache" vs "Restart apache2" in notify
   - Already uses modern FQCN for service module
   - Modern equivalent: Fix handler name consistency

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" → "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |
| Hard-coded paths | Parameterized variables | defaults/main.yml | Flexibility |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates present in current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `manage_apache_service`: boolean, default: true, description: "Whether to manage Apache service restarts"
- `manage_ssh_service`: boolean, default: true, description: "Whether to manage SSH service restarts"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted task with FQCN)
- handlers/main.yml (consistent handler names)
- defaults/main.yml (parameterized variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (input validation)

**Services to check**: 
- apache2 (should restart after SSL config change)
- sshd (should restart as specified)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration syntax
apache2ctl configtest

# Check SSL protocol configuration
openssl s_client -connect localhost:443 -tls1_2

# Verify services are running
systemctl status apache2
systemctl status sshd

# Test SSL configuration
nmap --script ssl-enum-ciphers -p 443 localhost
```

**Critical Migration Notes**:
1. **Handler Name Consistency**: The current playbook has a mismatch between the notify target ("Restart apache2") and the actual handler name ("Restart apache"). This must be fixed.
2. **Role Structure**: Convert from standalone playbook to proper role structure with separate task and handler files.
3. **Parameterization**: Hard-coded file paths should be moved to defaults/main.yml for flexibility.
4. **FQCN**: The `replace` module needs to be updated to `ansible.builtin.replace`.
5. **Boolean Values**: `become: yes` should be `become: true`.
6. **Security Context**: This role addresses the POODLE vulnerability (CVE-2014-3566) by disabling SSLv3 and older protocols.