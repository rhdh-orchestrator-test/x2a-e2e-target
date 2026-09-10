---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a traditional Ansible role structure. However, I can still provide a migration plan to modernize this into a proper Ansible role following current best practices.

# Migration Plan: poodle-fix-demo

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by updating Apache SSL configuration to disable older SSL protocols and enforce TLS 1.2. The main modernization needs include converting from a playbook to a proper role structure, fixing FQCN usage, correcting handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration in Apache to enforce TLS 1.2 only
- Manages Apache2 and SSH service restarts
- Replaces SSL protocol directives in Apache configuration files

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

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update Apache SSL configuration
   - **Step 2**: Targets `/etc/apache2/mods-available/ssl.conf` file
   - **Step 3**: Replaces any existing `SSLProtocol` directive with `SSLProtocol -all +TLSv1.2`
   - **Legacy patterns found**: Non-FQCN module name, handler naming inconsistency
   - **Modern equivalent**: Use `ansible.builtin.replace` with proper FQCN
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers):
   - **Handler inconsistency**: Task notifies "Restart apache2" but handler is named "Restart apache"
   - **Modern equivalent**: Consistent handler naming and proper service management

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache2" vs "Restart apache" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |
| Hardcoded paths | Parameterized variables | tasks/main.yml | `/etc/apache2/mods-available/ssl.conf` |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration directive"
- `apache_service_name`: string, default: "apache2", description: "Name of the Apache service"
- `ssh_service_name`: string, default: "sshd", description: "Name of the SSH service"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted task)
- handlers/main.yml (fixed handler names)
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

# Check current SSL configuration
grep -n "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify SSH service is running
systemctl status sshd

# Test SSL configuration after applying changes
openssl s_client -connect localhost:443 -tls1_2

# Verify POODLE vulnerability is fixed
nmap --script ssl-poodle localhost -p 443
```

**Critical Migration Notes:**
1. **Handler Naming Fix**: The task notifies "Restart apache2" but the handler is named "Restart apache" - this must be corrected for proper execution
2. **Path Parameterization**: The hardcoded Apache configuration path should be made configurable via variables
3. **Service Name Consistency**: Both apache2 and sshd services are managed but should be parameterized for different distributions
4. **Security Validation**: Post-migration testing should verify the POODLE vulnerability is actually resolved
5. **Idempotency**: The replace module is already idempotent, but testing should verify repeated runs don't cause issues