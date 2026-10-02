---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `chef-and-ansible/poodle_fix.yml` is actually a **playbook file**, not an Ansible role. However, I can still provide a migration plan to convert this playbook into a modern Ansible role structure and modernize its content.

# Migration Plan: poodle_fix

**TLDR**: This is currently a playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook to a proper role structure and modernized with current Ansible best practices including FQCN usage, proper handler naming consistency, and role organization.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
- Manages Apache2 and SSH service restarts
- Targets SSL configuration in `/etc/apache2/mods-available/ssl.conf`

## File Structure

**Current Structure** (Playbook):
```
poodle_fix.yml
```

**Target Role Structure** (To be created):
```
tasks/main.yml
handlers/main.yml
meta/main.yml
defaults/main.yml
```

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix Task** (`poodle_fix.yml`):
   - Uses `replace` module to update Apache SSL configuration
   - Targets `/etc/apache2/mods-available/ssl.conf`
   - Replaces any existing `SSLProtocol` directive with `SSLProtocol -all +TLSv1.2`
   - Uses legacy short module name `replace` instead of FQCN
   - Notifies two handlers for service restarts
   - Handler naming inconsistency: notifies "Restart apache2" but handler is named "Restart apache"

2. **Handlers** (`poodle_fix.yml`):
   - Two service restart handlers using modern FQCN `ansible.builtin.service`
   - Handler name mismatch: task notifies "Restart apache2" but handler is "Restart apache"
   - Both handlers properly use modern service module syntax

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | Fix "Restart apache" → "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing `mode:` parameter | Add `mode: '0644'` | tasks/main.yml | File permissions best practice |
| No argument specs | Create argument_specs.yml | meta/argument_specs.yml | Role validation |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates present in current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `apache_service_name`: string, default: "apache2", description: "Name of Apache service"
- `ssh_service_name`: string, default: "sshd", description: "Name of SSH service"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted from playbook)
- handlers/main.yml (extracted from playbook)
- meta/main.yml (new file with role metadata)
- defaults/main.yml (new file with default variables)
- meta/argument_specs.yml (new file for role validation)

**Services to check**: 
- apache2 service status and configuration
- sshd service status

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Check service status
systemctl status apache2
systemctl status sshd

# Test SSL configuration (if Apache is running)
openssl s_client -connect localhost:443 -tls1_2 < /dev/null

# Verify role syntax
ansible-playbook --syntax-check site.yml
ansible-lint roles/poodle_fix/
```

**Key Migration Steps:**
1. Create proper role directory structure
2. Move task content to `tasks/main.yml` with FQCN modernization
3. Extract handlers to `handlers/main.yml` and fix naming consistency
4. Create `defaults/main.yml` with configurable variables
5. Add `meta/main.yml` with role metadata and dependencies
6. Create `meta/argument_specs.yml` for role validation
7. Update boolean syntax from `yes` to `true`
8. Add proper file permissions where applicable
9. Test the converted role thoroughly before deployment