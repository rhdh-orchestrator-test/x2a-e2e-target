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

2. **Service Management** (`handlers section`):
   - **Step 1**: Restarts Apache2 and SSH services after configuration changes
   - **Step 2**: Legacy patterns: Inconsistent handler naming (`Restart apache` vs `Restart apache2` in notify)
   - **Step 3**: Modern equivalent: Consistent handler naming and proper FQCN usage
   - Ansible module mapping: Already using `ansible.builtin.service` (partially modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Hardcoded paths | Variables in defaults | tasks/main.yml | Parameterization |
| Handler name mismatch | Consistent naming | handlers/main.yml | Fix notify/handler mismatch |
| Playbook structure | Role structure | All files | Convert to proper role |
| Hardcoded SSL protocols | Configurable variables | tasks/main.yml | Make protocols configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (restarted after SSL config change)
- sshd (restarted after SSL config change)

## Template Modernization

No templates in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"
- `ssl_protocol_regex`: string, default: "^SSLProtocol.*$", description: "Regex pattern to match SSL protocol lines"
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
- apache2 (should restart successfully)
- sshd (should restart successfully)

**Templates to validate**: 
None

## Pre-flight checks:
```bash
# Verify Apache SSL module is enabled
apache2ctl -M | grep ssl

# Check Apache configuration syntax
apache2ctl configtest

# Verify SSL configuration file exists
test -f /etc/apache2/mods-available/ssl.conf

# Check current SSL protocol configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Test SSL configuration after change
openssl s_client -connect localhost:443 -tls1_2

# Verify services are running after restart
systemctl is-active apache2
systemctl is-active sshd
```

**Critical Migration Notes:**
1. **Handler Name Mismatch**: The current playbook has a critical bug - it notifies "Restart apache2" and "Restart sshd" but the handler is named "Restart apache". This needs to be fixed during migration.
2. **Security Focus**: This role specifically addresses the POODLE vulnerability (CVE-2014-3566) by disabling SSLv3 and older protocols.
3. **Service Dependencies**: Both Apache and SSH are restarted, which may indicate this was part of a broader SSL hardening effort.
4. **Path Assumptions**: The role assumes Debian/Ubuntu Apache structure (`/etc/apache2/`). Consider adding OS-specific path handling for broader compatibility.