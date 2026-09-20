---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not an Ansible role. However, the user has requested to analyze it for migration to a modern Ansible role. I'll create a migration plan to convert this playbook into a proper Ansible role structure with modern best practices.

# Migration Plan: poodle_fix

**TLDR**: This is currently a simple playbook that fixes SSL configuration in Apache to address the POODLE vulnerability by enforcing TLSv1.2. It needs to be converted from a playbook to a proper Ansible role structure and modernized with current best practices including FQCN usage, proper file organization, and enhanced configurability.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes SSL protocol configuration in Apache to mitigate POODLE vulnerability
- Replaces SSLProtocol directive to enforce TLSv1.2 only
- Restarts Apache2 and SSH services after configuration changes
- Currently targets `/etc/apache2/mods-available/ssl.conf` (Debian/Ubuntu systems)

## File Structure

**Current Structure** (Playbook):
```
poodle_fix.yml
```

**Target Role Structure**:
```
tasks/main.yml
handlers/main.yml
defaults/main.yml
meta/main.yml
meta/argument_specs.yml
templates/ssl.conf.j2
vars/main.yml
```

**Task Files:**
tasks/main.yml

**Handler Files:**
handlers/main.yml

**Variable Files:**
defaults/main.yml
vars/main.yml

**Meta:**
meta/main.yml
meta/argument_specs.yml

**Templates:**
templates/ssl.conf.j2

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Configuration Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, hardcoded paths, limited configurability
   - **Step 3**: Modern equivalent: Use FQCN `ansible.builtin.replace`, add variables for paths and protocols, improve idempotency
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Restart Handlers**:
   - **Step 1**: Restarts Apache2 and SSH services
   - **Step 2**: Legacy patterns: Handler name mismatch (task notifies "Restart apache2" but handler is named "Restart apache")
   - **Step 3**: Modern equivalent: Fix handler name consistency, use FQCN for service module
   - Ansible module mapping: Already uses `ansible.builtin.service` (partially modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Hardcoded paths | Variables with defaults | tasks/main.yml, defaults/main.yml | Configurability |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache2" vs "Restart apache" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing `changed_when` | Add idempotency checks | tasks/main.yml | Better change detection |
| Single protocol hardcoded | Configurable SSL protocols | tasks/main.yml, defaults/main.yml | Enhanced flexibility |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by system, not installed by role)
**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

**ssl.conf.j2**: Create a template for Apache SSL configuration to replace the simple regex replacement:
- Allow configurable SSL protocols
- Support multiple Apache distributions (Debian/Ubuntu, RHEL/CentOS)
- Include other SSL hardening options beyond just protocol selection

## Argument Specification

Variables for meta/argument_specs.yml:
- `apache_ssl_protocols`: list, default: ['-all', '+TLSv1.2'], description: "SSL protocols to enable/disable"
- `apache_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `restart_services`: list, default: ['apache2', 'sshd'], description: "Services to restart after SSL configuration change"
- `backup_config`: boolean, default: true, description: "Whether to backup original configuration file"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)
- templates/ssl.conf.j2 (SSL configuration template)

**Services to check**: 
- apache2 (configuration applied and service restarted)
- sshd (service restarted successfully)

**Templates to validate**: 
- ssl.conf.j2 (proper SSL protocol configuration)

## Pre-flight checks:
```bash
# Verify Apache is installed and running
systemctl status apache2

# Check current SSL configuration
grep -i "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify Apache configuration syntax after changes
apache2ctl configtest

# Test SSL configuration with OpenSSL
openssl s_client -connect localhost:443 -tls1_2

# Verify services are running after restart
systemctl status apache2 sshd
```

**Additional Migration Notes**:
1. The current playbook has a handler name mismatch that needs fixing
2. Consider adding support for different Linux distributions (RHEL uses `/etc/httpd/` instead of `/etc/apache2/`)
3. Add backup functionality before modifying configuration files
4. Include validation to ensure Apache SSL module is enabled
5. Consider adding more comprehensive SSL hardening beyond just protocol selection
6. Add proper error handling and rollback capabilities