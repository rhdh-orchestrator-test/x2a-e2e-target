---
source-path: chef-and-ansible/poodle_fix.yml
---

I can see that `poodle_fix.yml` is actually a playbook file, not a role structure. However, the user is asking me to analyze this as a module for migration to Ansible. Let me examine the content more carefully and treat this as a legacy Ansible playbook that needs to be converted into a modern Ansible role.

Based on my analysis, I can see this is a legacy Ansible playbook that performs SSL security hardening (specifically fixing the POODLE vulnerability). Let me create a migration plan to convert this into a modern Ansible role.

# Migration Plan: ssl-security-hardening

**TLDR**: This legacy playbook performs SSL security hardening by fixing the POODLE vulnerability in Apache SSL configuration. It needs modernization from a playbook format to a proper role structure with FQCN usage, proper handler naming consistency, and modern Ansible best practices.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache by updating SSL protocol configuration
- Disables all SSL protocols and enables only TLSv1.2
- Restarts Apache2 and SSH services after configuration changes
- Targets `/etc/apache2/mods-available/ssl.conf` configuration file

## File Structure

**Current Structure (Legacy Playbook):**
```
poodle_fix.yml
```

**Target Role Structure (Modern):**
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

1. **SSL Protocol Hardening** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: short module name, inconsistent handler naming
   - **Step 3**: Modern equivalent: FQCN module usage, consistent handler names, role structure
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent handler naming | handlers/main.yml | "Restart apache" vs "Restart apache2" |
| Playbook format | Role structure | All files | Convert to proper role |
| Inline parameters | Structured parameters | tasks/main.yml | Multi-line parameter formatting |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2, openssh-server (managed by system)
**Services managed**: 
- apache2 (restarted after SSL config change)
- sshd (restarted after SSL config change)

## Template Modernization

No templates present in the legacy playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_services`: list, default: ["apache2", "sshd"], description: "Services to restart after SSL configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (configurable variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (input validation)

**Services to check**: 
- apache2 (SSL configuration applied and service restarted)
- sshd (service restarted successfully)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest

# Check SSL protocol configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify services are running
systemctl status apache2
systemctl status sshd

# Test SSL configuration (if applicable)
openssl s_client -connect localhost:443 -tls1_2
```

**Key Migration Notes:**
1. **Handler Naming Inconsistency**: The legacy playbook has a mismatch between the notify target ("Restart apache2") and the actual handler name ("Restart apache"). This needs to be fixed for proper execution.

2. **Security Focus**: This role specifically addresses the POODLE vulnerability (CVE-2014-3566) by disabling SSLv3 and older protocols, enforcing only TLSv1.2.

3. **Service Dependencies**: Both Apache and SSH services are restarted, suggesting this might be part of a broader security hardening playbook that affects multiple services.

4. **Configuration Path**: The role targets Debian/Ubuntu Apache configuration structure (`/etc/apache2/mods-available/ssl.conf`). Consider adding OS-specific variable support for broader compatibility.

5. **Idempotency**: The `replace` module is naturally idempotent, so no additional `changed_when` conditions are needed.