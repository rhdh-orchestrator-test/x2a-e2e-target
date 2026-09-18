---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role. However, I can analyze it for modernization needs and provide a migration plan to convert it into a proper modern Ansible role structure.

# Migration Plan: poodle-ssl-fix

**TLDR**: This is currently a standalone playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook into a proper role structure and modernized with current Ansible best practices including FQCN usage, proper handler naming consistency, and role organization.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
- Restarts Apache2 and SSH services after configuration changes
- Targets Apache2 SSL module configuration

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
defaults/main.yml
meta/argument_specs.yml
```

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Targets `/etc/apache2/mods-available/ssl.conf` file
   - **Step 3**: Replaces any existing `SSLProtocol` directive with secure TLSv1.2 only
   - **Legacy patterns found**: Non-FQCN module name, handler name inconsistency
   - **Modern equivalent**: Use `ansible.builtin.replace` with consistent handler naming
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" vs "Restart apache2" in notify |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing file mode | Add mode parameter | tasks/main.yml | File operation best practice |
| No argument specs | Add meta/argument_specs.yml | meta/ | Role validation |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (restarted after SSL config change)
- sshd (restarted after SSL config change)

## Template Modernization

No templates present in current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable"
- `restart_services`: list, default: ["apache2", "sshd"], description: "Services to restart after SSL configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted from playbook tasks)
- handlers/main.yml (extracted handlers with consistent naming)
- defaults/main.yml (parameterized configuration)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (input validation)

**Services to check**: 
- apache2 (SSL configuration applied and service restarted)
- sshd (service restarted successfully)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL module is enabled
apache2ctl -M | grep ssl

# Check SSL configuration syntax
apache2ctl configtest

# Verify SSL protocols after change
openssl s_client -connect localhost:443 -tls1_2

# Verify services are running
systemctl status apache2
systemctl status sshd

# Test POODLE vulnerability is fixed
nmap --script ssl-poodle localhost -p 443
```

**Key Migration Notes**:
1. **Handler Inconsistency**: The notify calls "Restart apache2" but handler is named "Restart apache" - this needs to be fixed
2. **Playbook to Role Conversion**: This is currently a playbook targeting specific hosts, needs conversion to reusable role
3. **Parameterization**: Hard-coded paths and protocols should be variables with sensible defaults
4. **Security Validation**: Should add tasks to verify the fix was applied correctly
5. **Idempotency**: The replace module is already idempotent, but consider adding validation tasks