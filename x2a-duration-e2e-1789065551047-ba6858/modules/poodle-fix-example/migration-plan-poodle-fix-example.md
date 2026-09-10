---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a traditional Ansible role structure. However, I can still provide a migration plan to modernize this into a proper Ansible role following current best practices.

# Migration Plan: poodle-fix-example

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by updating Apache SSL configuration to disable vulnerable protocols and enforce TLS 1.2. The main modernization needs include converting from a playbook to a proper role structure, adding FQCN to modules, fixing handler naming inconsistencies, and implementing proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration in Apache
- Disables vulnerable SSL protocols (-all)
- Enforces TLS 1.2 only (+TLSv1.2)
- Restarts Apache and SSH services to apply changes

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
   - **Step 1**: Updates Apache SSL configuration to fix POODLE vulnerability
   - **Step 2**: Uses `replace` module to modify SSL protocol settings
   - **Step 3**: Notifies handlers to restart services
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **handlers** (`handlers/main.yml`):
   - **Handler inconsistency**: Playbook notifies "Restart apache2" and "Restart sshd" but defines "Restart apache" and "Restart sshd"
   - Both handlers use modern FQCN already (`ansible.builtin.service`)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Fix notification names | tasks/main.yml, handlers/main.yml | "apache2" vs "apache" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |
| Hardcoded paths | Parameterize paths | tasks/main.yml | Make configurable |

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
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration change"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted from playbook)
- handlers/main.yml (extracted from playbook)
- defaults/main.yml (new file with default variables)
- meta/main.yml (new role metadata)
- meta/argument_specs.yml (new argument specifications)

**Services to check**: 
- apache2 service status and configuration
- sshd service status

**Templates to validate**: 
None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
systemctl status apache2
apache2ctl -M | grep ssl

# Check current SSL configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Test SSL configuration after changes
openssl s_client -connect localhost:443 -tls1_2

# Verify SSH service is running
systemctl status sshd

# Test role syntax
ansible-playbook --syntax-check site.yml

# Run role in check mode
ansible-playbook --check site.yml
```

**Key Migration Notes:**
1. **Handler Name Fix**: The original playbook has a critical bug where it notifies "Restart apache2" but the handler is named "Restart apache". This must be fixed during migration.
2. **Parameterization**: Hardcoded paths and configuration values should be moved to defaults/main.yml for flexibility.
3. **Role Structure**: Convert from a single playbook file to proper role directory structure.
4. **Security Context**: This role addresses CVE-2014-3566 (POODLE attack) by disabling SSLv3 and enforcing TLS 1.2.
5. **Service Dependencies**: Both Apache and SSH restarts are included, suggesting this might be part of a broader security hardening effort.