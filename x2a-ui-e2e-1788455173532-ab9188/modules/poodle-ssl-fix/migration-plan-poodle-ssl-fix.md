---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role structure. Let me provide the migration specification for converting this playbook into a modern Ansible role.

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2 protocol. The main modernization needs include converting from playbook to role structure, updating module syntax to use FQCN, fixing handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Configures Apache SSL protocol settings to disable vulnerable SSL protocols
- Replaces SSLProtocol configuration in Apache ssl.conf to use only TLS 1.2
- Manages Apache2 and SSH service restarts after configuration changes
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

1. **SSL Protocol Configuration** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: short module name, handler naming inconsistency
   - **Step 3**: Modern equivalent: FQCN module name, consistent handler naming
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" vs "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| Hardcoded paths | Variables | tasks/main.yml | Make paths configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by system)
**Services managed**: 
- apache2 (restarted after configuration change)
- sshd (restarted after configuration change)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
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

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and ssl module is available
apache2ctl -M | grep ssl
# Check current SSL configuration
grep SSLProtocol /etc/apache2/mods-available/ssl.conf
# Test Apache configuration syntax
apache2ctl configtest
# Verify services are running
systemctl status apache2
systemctl status sshd
# Test SSL configuration after change
openssl s_client -connect localhost:443 -tls1_2
```

**Key Migration Notes:**
1. **Handler Naming Issue**: The current playbook has a mismatch between the notify target ("Restart apache2") and the actual handler name ("Restart apache"). This needs to be fixed for consistency.
2. **Hardcoded Paths**: The Apache configuration path is hardcoded and should be made configurable through variables.
3. **Security Focus**: This role specifically addresses the POODLE vulnerability (CVE-2014-3566) by disabling SSL 3.0 and older protocols.
4. **Service Dependencies**: Both Apache and SSH services are restarted, which may indicate this was part of a broader security hardening effort.
5. **Role Conversion**: The current playbook structure needs to be converted to a proper Ansible role with separated concerns (tasks, handlers, variables, metadata).