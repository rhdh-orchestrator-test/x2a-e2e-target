---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role structure. However, I can analyze it for modernization needs and provide a migration plan to convert it into a proper modern Ansible role.

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2 protocol. The main modernization needs include converting from a playbook to a proper role structure, fixing FQCN usage, correcting handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Configures Apache to use only TLS 1.2 protocol
- Restarts Apache2 and SSH services after configuration changes
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

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Configuration** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Replaces any existing SSLProtocol directive with secure TLS 1.2 only
   - **Step 3**: Notifies handlers to restart services
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Restart Handlers**:
   - **Handler 1**: Restarts Apache2 service (already uses FQCN)
   - **Handler 2**: Restarts SSH service (already uses FQCN)
   - **Issue**: Handler naming inconsistency - notifies "Restart apache2" but handler is named "Restart apache"

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Fix handler names | handlers/main.yml | "Restart apache2" vs "Restart apache" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Hard-coded paths | Variables | tasks/main.yml | `/etc/apache2/mods-available/ssl.conf` |
| Hard-coded protocols | Variables | tasks/main.yml | `TLSv1.2` should be configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core modules)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2
- sshd

## Template Modernization

No templates present in current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration change"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**: 
- apache2 (should be running and using TLS 1.2 only)
- sshd (should be running)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and running
systemctl status apache2

# Check current SSL configuration
grep -i "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Test SSL configuration after change
openssl s_client -connect localhost:443 -tls1_2

# Verify no SSL 3.0 or TLS 1.0/1.1 support
openssl s_client -connect localhost:443 -ssl3 2>&1 | grep -i "handshake failure"
openssl s_client -connect localhost:443 -tls1 2>&1 | grep -i "handshake failure"
openssl s_client -connect localhost:443 -tls1_1 2>&1 | grep -i "handshake failure"

# Verify SSH service is running
systemctl status sshd
```

**Critical Issues Found:**
1. **Handler Naming Mismatch**: The task notifies "Restart apache2" but the handler is named "Restart apache"
2. **Missing FQCN**: The `replace` module needs to be `ansible.builtin.replace`
3. **Boolean Syntax**: `become: yes` should be `become: true`
4. **Hard-coded Values**: Configuration paths and SSL protocols should be variables
5. **Structure**: This is a playbook that should be converted to a proper role structure
6. **Missing Validation**: No checks to ensure Apache SSL module is enabled before configuration

**Recommended Modern Role Structure:**

**tasks/main.yml:**
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: "{{ apache_ssl_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol {{ ssl_protocols }}'
  notify:
    - restart apache2
    - restart sshd
  become: true
```

**handlers/main.yml:**
```yaml
---
- name: restart apache2
  ansible.builtin.service:
    name: apache2
    state: restarted
  when: restart_apache | bool

- name: restart sshd
  ansible.builtin.service:
    name: sshd
    state: restarted
  when: restart_sshd | bool
```

This migration addresses the POODLE vulnerability while following modern Ansible best practices and providing proper configurability.