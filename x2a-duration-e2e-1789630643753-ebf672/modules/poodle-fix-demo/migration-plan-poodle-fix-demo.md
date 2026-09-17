---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `chef-and-ansible/poodle_fix.yml` is not actually an Ansible role but rather a standalone playbook. However, I can still provide a migration plan to convert this playbook into a modern Ansible role structure. Let me analyze the content and provide the migration specification.

# Migration Plan: poodle-fix-demo

**TLDR**: This is currently a standalone playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook into a proper Ansible role structure and modernized to follow current best practices including FQCN usage, proper handler naming consistency, and role organization.

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

**Target Role Structure** (to be created):
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
   - Uses `replace` module to update SSL protocol configuration
   - Targets `/etc/apache2/mods-available/ssl.conf`
   - Replaces any existing `SSLProtocol` directive with `SSLProtocol -all +TLSv1.2`
   - Uses regex pattern `^SSLProtocol.*$` for matching
   - Notifies both Apache2 and SSH service restarts
   - Legacy patterns: Missing FQCN, inconsistent handler naming

2. **Handler Section** (`poodle_fix.yml`):
   - Two handlers for service restarts
   - Handler naming inconsistency: "Restart apache2" vs "Restart apache"
   - One handler already uses FQCN (`ansible.builtin.service`)
   - One handler missing (referenced "Restart apache2" but defined "Restart apache")

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache2" handler missing |
| Playbook structure | Role structure | All files | Convert to proper role |
| Hardcoded paths | Parameterized variables | tasks/main.yml | Use variables for file paths |
| Missing argument specs | Add validation | meta/argument_specs.yml | Role input validation |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

No templates present in current playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration change"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted task)
- handlers/main.yml (fixed handler names)
- defaults/main.yml (parameterized variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (input validation)

**Services to check**: 
- apache2 (should restart successfully)
- sshd (should restart successfully)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration syntax
apache2ctl configtest

# Check SSL protocol configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify Apache service status
systemctl status apache2

# Verify SSH service status  
systemctl status sshd

# Test SSL configuration with openssl
echo | openssl s_client -connect localhost:443 -tls1_2 2>/dev/null | grep "Protocol"
```

## Critical Issues to Address

1. **Handler Name Mismatch**: The task notifies "Restart apache2" but the handler is named "Restart apache" - this will cause the handler to never execute
2. **Missing Role Structure**: Convert from playbook to proper role organization
3. **Hardcoded Values**: Parameterize file paths and configuration values
4. **FQCN Compliance**: Update `replace` module to use `ansible.builtin.replace`
5. **Boolean Modernization**: Change `become: yes` to `become: true`
6. **Add Validation**: Implement argument specifications for role inputs
7. **Error Handling**: Add validation to ensure Apache configuration is valid before restart