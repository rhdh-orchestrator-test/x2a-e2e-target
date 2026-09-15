---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `chef-and-ansible/poodle_fix.yml` is actually a **playbook file**, not an Ansible role. However, I can still provide a migration plan to convert this legacy playbook into a modern Ansible role structure. Let me analyze the content and provide the migration specification.

# Migration Plan: poodle_fix

**TLDR**: This is a legacy Ansible playbook (not a role) that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. The migration involves converting it to a proper role structure and modernizing several legacy patterns including module FQCN usage, handler naming inconsistencies, and adding proper role metadata.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols and enable only TLSv1.2
- Manages Apache2 and SSH service restarts
- Modifies `/etc/apache2/mods-available/ssl.conf` configuration file

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

**Task Files:**
tasks/main.yml

**Handler Files:**
handlers/main.yml

**Variable Files:**
defaults/main.yml

**Meta:**
meta/main.yml
meta/argument_specs.yml

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update SSL protocol configuration in Apache
   - **Step 2**: Legacy patterns found: missing FQCN for `replace` module, inconsistent handler naming
   - **Step 3**: Modern equivalent: use `ansible.builtin.replace` with proper FQCN, consistent handler naming
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers):
   - **Step 1**: Restarts Apache2 and SSH services after configuration changes
   - **Step 2**: Legacy patterns found: handler name mismatch (`Restart apache2` vs `Restart apache`), already using FQCN
   - **Step 3**: Modern equivalent: fix handler name consistency, maintain FQCN usage

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `notify: - Restart apache2` with `name: Restart apache` | Consistent naming | handlers/main.yml | Handler name mismatch |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing role metadata | Add meta/main.yml | meta/main.yml | Role information |
| No argument specification | Add argument_specs.yml | meta/argument_specs.yml | Variable validation |
| Hardcoded paths | Parameterize paths | defaults/main.yml, tasks/main.yml | Flexibility |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2
- sshd

## Template Modernization

No templates present in the current playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration change"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable specifications)
- defaults/main.yml (default variables)

**Services to check**: 
- apache2 (should restart successfully)
- sshd (should restart successfully)

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

**Critical Issues Found:**
1. **Handler Name Mismatch**: The task notifies `Restart apache2` but the handler is named `Restart apache`
2. **Missing FQCN**: The `replace` module should be `ansible.builtin.replace`
3. **Playbook vs Role**: Current structure is a playbook, needs conversion to role format
4. **Hardcoded Paths**: Configuration file path should be parameterized
5. **No Error Handling**: Missing validation for configuration file existence
6. **No Backup**: Should backup original configuration before modification

**Additional Modernization Recommendations:**
1. Add `backup: yes` parameter to the replace task
2. Add validation task to check if Apache configuration is valid before restart
3. Use `ansible.builtin.stat` to verify configuration file exists before modification
4. Add tags for selective execution
5. Consider using `ansible.builtin.lineinfile` with validation instead of `replace` for more precise control