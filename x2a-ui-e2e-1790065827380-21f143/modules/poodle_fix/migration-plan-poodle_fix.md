---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, `chef-and-ansible/poodle_fix.yml` is not an Ansible role but rather a standalone playbook. However, I can analyze it for modernization and provide guidance on converting it to a proper role structure. Let me provide the migration analysis:

# Migration Plan: poodle_fix

**TLDR**: This is currently a standalone playbook (not a role) that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. The main modernization needs include converting to proper role structure, fixing handler naming inconsistency, adding proper file permissions, and implementing modern Ansible practices.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
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
meta/main.yml
defaults/main.yml
```

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, missing file permissions, handler naming mismatch
   - **Step 3**: Modern equivalent: Use FQCN `ansible.builtin.replace`, add proper file permissions, fix handler names
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Restart Handlers**:
   - **Handler Issue**: Task notifies "Restart apache2" but handler is named "Restart apache"
   - **Missing Handler**: Task notifies "Restart sshd" but this handler exists
   - **Modernization**: Already uses FQCN for service module

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Fix handler names | handlers/main.yml | "Restart apache2" vs "Restart apache" |
| Missing file mode | Add `mode: '0644'` | tasks/main.yml | File permissions best practice |
| Playbook structure | Convert to role | All files | Proper role organization |
| Missing changed_when | Add idempotency check | tasks/main.yml | Better change detection |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core modules)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

No templates present in current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `apache_service_name`: string, default: "apache2", description: "Name of Apache service"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after SSL changes"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted from playbook)
- handlers/main.yml (extracted handlers with fixed names)
- meta/main.yml (new role metadata)
- defaults/main.yml (new default variables)

**Services to check**: 
- apache2 service status and SSL configuration
- sshd service status

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest
sudo systemctl status apache2

# Test SSL protocol configuration
openssl s_client -connect localhost:443 -tls1_2

# Verify SSH service
sudo systemctl status sshd

# Check Apache SSL module is loaded
apache2ctl -M | grep ssl
```

**Critical Issues to Address:**
1. **Handler Name Mismatch**: The task notifies "Restart apache2" but the handler is named "Restart apache" - this will cause the handler to never execute
2. **Playbook vs Role**: Current file is a playbook, not a role - needs complete restructuring
3. **Missing File Permissions**: The replace task should specify file mode for security
4. **No Idempotency Check**: Should add validation that the change is actually needed
5. **Hard-coded Paths**: Configuration file path should be parameterized for different distributions

**Recommended Modern Role Structure:**
```yaml
# tasks/main.yml
- name: Update Apache SSL protocol configuration
  ansible.builtin.replace:
    dest: "{{ ssl_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "{{ ssl_protocol_config }}"
    mode: '0644'
    backup: true
  notify:
    - restart apache2
    - restart sshd
  when: ssl_config_path is file

# handlers/main.yml  
- name: restart apache2
  ansible.builtin.service:
    name: "{{ apache_service_name }}"
    state: restarted

- name: restart sshd
  ansible.builtin.service:
    name: sshd
    state: restarted
  when: restart_sshd | bool
```