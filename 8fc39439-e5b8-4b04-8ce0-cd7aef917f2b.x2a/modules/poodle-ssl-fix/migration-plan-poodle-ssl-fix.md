---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a traditional Ansible role structure. However, I can provide a migration plan to convert this into a modern Ansible role. Let me provide the detailed migration specification:

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLSv1.2 protocol. The main modernization needs include converting from a playbook to a proper role structure, using FQCN for modules, fixing handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Modifies Apache SSL configuration to disable vulnerable protocols
- Enforces TLSv1.2 as the only allowed SSL/TLS protocol
- Restarts Apache and SSH services after configuration changes

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

The role performs operations in this order:

1. **main.yml** (`tasks/main.yml`):
   - **Step 1**: Fixes Apache SSL configuration by replacing SSLProtocol directive
   - **Step 2**: Uses `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - **Step 3**: Notifies handlers to restart services
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **handlers** (`handlers/main.yml`):
   - **Handler inconsistency**: Playbook notifies "Restart apache2" but handler is named "Restart apache"
   - **Step 1**: Restarts Apache2 service using `ansible.builtin.service`
   - **Step 2**: Restarts SSH service using `ansible.builtin.service`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Fix notification names | tasks/main.yml, handlers/main.yml | "Restart apache2" vs "Restart apache" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |
| Hard-coded paths | Parameterize paths | tasks/main.yml | Make configurable |
| Missing mode parameter | Add file permissions | tasks/main.yml | If file operations added |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2
- sshd

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration change"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted from playbook)
- handlers/main.yml (extracted from playbook)
- defaults/main.yml (new file with variables)
- meta/main.yml (new file with role metadata)
- meta/argument_specs.yml (new file with argument validation)

**Services to check**: 
- apache2 service status and configuration
- sshd service status

**Templates to validate**: 
- None (no templates in this role)

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
systemctl is-active apache2

# Check current SSL configuration
grep -n "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify SSH service is running
systemctl is-active sshd

# Test SSL configuration after role execution
openssl s_client -connect localhost:443 -tls1_2 -quiet

# Verify POODLE vulnerability is fixed
nmap --script ssl-poodle localhost -p 443
```

**Critical Issues to Address:**
1. **Handler Name Mismatch**: The task notifies "Restart apache2" but the handler is named "Restart apache" - this will cause the handler to never execute
2. **Playbook to Role Conversion**: Current file is a playbook, needs complete restructuring into role format
3. **Hard-coded Paths**: Apache configuration path should be parameterized for different distributions
4. **Missing Error Handling**: No validation that Apache SSL module is enabled before attempting configuration
5. **Security Validation**: Should add tasks to verify the fix was applied correctly

**Additional Modernization Recommendations:**
- Add pre-task validation to ensure Apache and SSL module are installed
- Add post-task validation to verify SSL configuration is correct
- Consider adding support for multiple web servers (nginx, etc.)
- Add tags for selective execution
- Include backup of original configuration before modification