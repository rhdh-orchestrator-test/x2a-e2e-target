---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role. However, I can analyze it for modernization needs and provide a migration plan to convert it into a proper modern Ansible role structure.

# Migration Plan: poodle-ssl-fix

**TLDR**: This is currently a single playbook file that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook into a proper role structure and modernized with current Ansible best practices including FQCN usage, proper handler naming consistency, and role organization.

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
meta/main.yml
meta/argument_specs.yml
defaults/main.yml
README.md
```

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix Task** (`poodle_fix.yml`):
   - Uses `replace` module to update Apache SSL configuration
   - Targets `/etc/apache2/mods-available/ssl.conf`
   - Replaces any existing `SSLProtocol` directive with `SSLProtocol -all +TLSv1.2`
   - Uses regex pattern `^SSLProtocol.*$` to match existing SSL protocol lines
   - Notifies both Apache2 and SSH restart handlers
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Handler Operations** (`poodle_fix.yml`):
   - **Restart apache**: Uses modern FQCN `ansible.builtin.service` (already modernized)
   - **Restart sshd**: Uses modern FQCN `ansible.builtin.service` (already modernized)
   - **Issue**: Handler names are inconsistent with notify calls

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN required |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | poodle_fix.yml | "Restart apache2" vs "Restart apache" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing argument specs | Add meta/argument_specs.yml | New file | Role validation |
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

No templates present in current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration change"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted from playbook tasks)
- handlers/main.yml (extracted handlers with corrected names)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (argument validation)
- defaults/main.yml (default variables)

**Services to check**: 
- apache2 service status and configuration
- sshd service status

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
systemctl status apache2

# Verify SSH daemon is running
systemctl status sshd

# Test SSL configuration syntax
apache2ctl configtest

# Verify SSL protocol configuration after change
openssl s_client -connect localhost:443 -tls1_2 < /dev/null

# Check that vulnerable protocols are disabled
openssl s_client -connect localhost:443 -ssl3 < /dev/null 2>&1 | grep "handshake failure"
```

**Critical Issues Found:**
1. **Handler Name Mismatch**: The task notifies "Restart apache2" but the handler is named "Restart apache"
2. **Missing FQCN**: The `replace` module needs to be `ansible.builtin.replace`
3. **Boolean Syntax**: `become: yes` should be `become: true`
4. **Playbook vs Role**: Current structure is a playbook, needs conversion to proper role structure
5. **Hard-coded Paths**: SSL configuration path should be parameterized for flexibility
6. **Missing Validation**: No argument specifications for role parameters

**Modernization Priority:**
1. Fix handler name consistency (critical - will cause task failures)
2. Add FQCN to replace module
3. Convert playbook structure to role structure
4. Add parameterization for configuration paths
5. Add argument specifications for validation