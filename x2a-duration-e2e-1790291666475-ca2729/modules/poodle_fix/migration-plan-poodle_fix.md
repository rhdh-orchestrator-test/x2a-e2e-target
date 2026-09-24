---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook, not a role. However, the user has requested to analyze it for migration to a modern Ansible role. I'll create a migration plan to convert this playbook into a proper Ansible role with modern best practices.

# Migration Plan: poodle_fix

**TLDR**: This is currently a simple playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook to a proper Ansible role structure and modernized with current best practices including FQCN usage, proper variable management, and role structure.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
- Manages Apache2 and SSH service restarts
- Targets SSL configuration in `/etc/apache2/mods-available/ssl.conf`

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
   - **Step 2**: Legacy patterns found: non-FQCN module name, hardcoded paths, mixed handler naming
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with variables for paths and protocols
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (`handlers` section):
   - **Step 1**: Restarts Apache2 and SSH services after configuration changes
   - **Step 2**: Legacy patterns: Inconsistent handler naming ("Restart apache" vs "Restart apache2" in notify)
   - **Step 3**: Modern equivalent: Consistent handler naming, proper FQCN usage
   - Ansible module mapping: Already uses `ansible.builtin.service` (modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Hardcoded paths | Variables in defaults | tasks/main.yml | Parameterization |
| Playbook structure | Role structure | All files | Convert to role |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" → "Restart apache2" |
| Inline parameters | Multi-line YAML | tasks/main.yml | Readability |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by system, not installed by role)
**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

No templates present in the current playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocols`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocols configuration string"
- `ssl_protocol_regex`: string, default: "^SSLProtocol.*$", description: "Regex pattern to match existing SSL protocol configuration"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (should restart after SSL config change)
- sshd (should restart after SSL config change)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest

# Check SSL protocol configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify Apache service status
systemctl status apache2

# Verify SSH service status
systemctl status sshd

# Test SSL configuration (if applicable)
openssl s_client -connect localhost:443 -tls1_2
```

**Additional Migration Notes:**
1. The current playbook has a handler naming inconsistency - it notifies "Restart apache2" but the handler is named "Restart apache"
2. The role should be made more flexible by parameterizing the Apache configuration path and SSL protocol settings
3. Consider adding validation tasks to verify the SSL configuration is correct before applying changes
4. The role should include proper error handling for cases where Apache is not installed or the configuration file doesn't exist
5. Add tags for selective execution (e.g., `ssl`, `security`, `apache`)