---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I understand - this is a standalone playbook file, not a role structure. Let me analyze this playbook for migration to a modern Ansible role structure.

# Migration Plan: poodle_fix

**TLDR**: This is a standalone playbook that fixes the POODLE SSL vulnerability in Apache by enforcing TLSv1.2. It needs to be converted into a proper Ansible role structure and modernized with FQCN module names, proper boolean syntax, and handler name consistency. The playbook currently has a critical bug where the handler names don't match the notify directives.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability (CVE-2014-3566) in Apache web server
- Modifies Apache SSL configuration to enforce TLSv1.2 protocol only
- Restarts Apache2 service to apply changes
- Restarts SSHD service (appears to be a secondary security hardening step)
- Targets Apache2 on Debian/Ubuntu-based systems (`/etc/apache2/` path structure)

## File Structure

**Current Structure (Standalone Playbook):**
```
poodle_fix.yml
```

**Target Modern Role Structure:**
```
roles/poodle_fix/tasks/main.yml
roles/poodle_fix/handlers/main.yml
roles/poodle_fix/defaults/main.yml
roles/poodle_fix/meta/main.yml
roles/poodle_fix/meta/argument_specs.yml
roles/poodle_fix/README.md
```

## Module Explanation

The playbook performs operations in this order:

1. **SSL Protocol Hardening** (`poodle_fix.yml` - tasks section):
   - Uses `replace:` module (legacy short name) to modify Apache SSL configuration
   - Target file: `/etc/apache2/mods-available/ssl.conf`
   - Regex pattern: `^SSLProtocol.*$`
   - Replacement: `SSLProtocol -all +TLSv1.2`
   - Legacy patterns found:
     - Short module name `replace:` → should be `ansible.builtin.replace:`
     - Uses `become: yes` (legacy boolean) → should be `become: true`
     - Inline parameters without proper YAML structure
     - Handler name mismatch: notifies `Restart apache2` but handler is named `Restart apache`
   - Modern equivalent:
     - Use FQCN `ansible.builtin.replace:`
     - Proper YAML multi-line parameter format
     - Fix handler name consistency
     - Add validation checks

2. **Service Restart Handlers** (`poodle_fix.yml` - handlers section):
   - Restarts Apache2 service using `ansible.builtin.service:` (already modernized)
   - Restarts SSHD service using `ansible.builtin.service:` (already modernized)
   - **CRITICAL BUG**: Handler named `Restart apache` but task notifies `Restart apache2`
   - Modern equivalent:
     - Fix handler name to match notify directive
     - Consider making service names configurable variables

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `become: yes` | `become: true` | poodle_fix.yml | Boolean modernization |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN required |
| Inline parameters | Multi-line YAML | poodle_fix.yml | Readability and structure |
| Handler name mismatch | Fix naming consistency | poodle_fix.yml | **CRITICAL BUG** - `Restart apache2` notify → `Restart apache` handler |
| Hardcoded paths | Variables with defaults | poodle_fix.yml | Make configurable |
| Hardcoded SSL protocol | Configurable variable | poodle_fix.yml | Allow TLSv1.2/TLSv1.3 options |
| No validation | Add backup & validation | N/A | Add `backup: true` and config test |
| Standalone playbook | Role structure | All | Convert to proper role |
| No argument specs | Add argument_specs.yml | N/A | Define role inputs |
| No meta information | Add meta/main.yml | N/A | Document role metadata |

## Dependencies

**Collection dependencies** (for requirements.yml):
```yaml
collections:
  - name: ansible.builtin
    version: ">=2.10"
```

**Role dependencies**: None (standalone security hardening)

**External packages**: 
- apache2 (must be pre-installed)
- apache2 ssl module must be enabled

**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

No templates in current playbook. Consider adding:
- **ssl-hardening.conf.j2**: Template for SSL protocol configuration to allow more flexible security settings beyond just Apache

## Argument Specification

Variables that should be defined in `meta/argument_specs.yml`:

```yaml
argument_specs:
  main:
    short_description: Fix POODLE SSL vulnerability in Apache
    description:
      - Configures Apache to disable SSLv3 and enforce modern TLS protocols
      - Fixes CVE-2014-3566 (POODLE vulnerability)
    options:
      poodle_fix_apache_ssl_config_path:
        type: path
        default: /etc/apache2/mods-available/ssl.conf
        description: Path to Apache SSL configuration file
      poodle_fix_ssl_protocol:
        type: str
        default: '-all +TLSv1.2'
        description: SSL protocol configuration string for Apache
      poodle_fix_restart_apache:
        type: bool
        default: true
        description: Whether to restart Apache after configuration change
      poodle_fix_restart_sshd:
        type: bool
        default: true
        description: Whether to restart SSHD after configuration change
      poodle_fix_apache_service_name:
        type: str
        default: apache2
        description: Name of the Apache service (apache2 for Debian/Ubuntu, httpd for RHEL/CentOS)
      poodle_fix_backup_config:
        type: bool
        default: true
        description: Whether to backup configuration file before modification
      poodle_fix_validate_config:
        type: bool
        default: true
        description: Whether to validate Apache configuration before restarting
```

Variables for `defaults/main.yml`:
```yaml
# Apache SSL configuration
poodle_fix_apache_ssl_config_path: /etc/apache2/mods-available/ssl.conf
poodle_fix_ssl_protocol: '-all +TLSv1.2'

# Service management
poodle_fix_apache_service_name: apache2
poodle_fix_restart_apache: true
poodle_fix_restart_sshd: true

# Safety options
poodle_fix_backup_config: true
poodle_fix_validate_config: true
```

## Checks for the Migration

**Files to verify**: 
- `roles/poodle_fix/tasks/main.yml` - Main task file with modernized syntax
- `roles/poodle_fix/handlers/main.yml` - Handler definitions with correct names
- `roles/poodle_fix/defaults/main.yml` - Default variables
- `roles/poodle_fix/meta/main.yml` - Role metadata
- `roles/poodle_fix/meta/argument_specs.yml` - Argument specifications
- `roles/poodle_fix/README.md` - Documentation

**Services to check**: 
- apache2 (or httpd on RHEL-based systems)
- sshd

**Configuration files to validate**:
- `/etc/apache2/mods-available/ssl.conf` (Debian/Ubuntu)
- `/etc/httpd/conf.d/ssl.conf` (RHEL/CentOS - for extended platform support)

## Pre-flight checks:

```bash
# 1. Verify Apache is installed
ansible-playbook verify.yml --tags check_apache

# 2. Backup current SSL configuration
ansible-playbook verify.yml --tags backup_config

# 3. Test Apache configuration syntax after change
apache2ctl configtest  # Debian/Ubuntu
httpd -t              # RHEL/CentOS

# 4. Verify SSL protocol settings after migration
openssl s_client -connect localhost:443 -ssl3  # Should fail
openssl s_client -connect localhost:443 -tls1_2 # Should succeed

# 5. Check Apache service status
systemctl status apache2  # or httpd

# 6. Verify SSHD service is running
systemctl status sshd

# 7. Test Apache serves content after restart
curl -k https://localhost/

# 8. Verify no SSLv3 in configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf
```

## Critical Issues to Address

1. **Handler Name Mismatch (CRITICAL BUG)**: 
   - Task notifies: `Restart apache2`
   - Handler named: `Restart apache`
   - **This will cause the handler to never be called, leaving Apache not restarted**
   - Fix: Rename handler to `Restart apache2` or change notify to `Restart apache`

2. **Platform Compatibility**:
   - Current playbook hardcodes Debian/Ubuntu paths (`/etc/apache2/`)
   - RHEL/CentOS uses `/etc/httpd/` and service name `httpd`
   - Add platform detection and conditional paths

3. **No Configuration Validation**:
   - Should add `backup: true` to replace module
   - Should validate Apache config before restarting: `apache2ctl configtest`
   - Should use `block`/`rescue` for rollback capability

4. **Security Consideration**:
   - TLSv1.2 is good for 2014, but modern systems should support TLSv1.3
   - Consider: `SSLProtocol -all +TLSv1.2 +TLSv1.3`

5. **Missing Idempotency Checks**:
   - Should verify Apache service is enabled
   - Should check if SSL module is loaded before modifying config

6. **SSHD Restart Rationale**:
   - Unclear why SSHD is restarted for Apache SSL fix
   - If this is for SSH POODLE fix, it should be a separate task/role
   - Consider making this optional or removing if not needed

## Recommended Modern Role Structure

**tasks/main.yml**:
```yaml
---
- name: Ensure Apache is installed
  ansible.builtin.package:
    name: "{{ poodle_fix_apache_service_name }}"
    state: present
  tags: ['poodle_fix', 'apache']

- name: Fix POODLE vulnerability in Apache SSL configuration
  ansible.builtin.replace:
    path: "{{ poodle_fix_apache_ssl_config_path }}"
    regexp: '^SSLProtocol.*$'
    replace: 'SSLProtocol {{ poodle_fix_ssl_protocol }}'
    backup: "{{ poodle_fix_backup_config }}"
    validate: 'apache2ctl -f %s -t'
  notify:
    - Restart apache2
    - Restart sshd
  tags: ['poodle_fix', 'apache', 'ssl']

- name: Ensure Apache is enabled and started
  ansible.builtin.service:
    name: "{{ poodle_fix_apache_service_name }}"
    state: started
    enabled: true
  tags: ['poodle_fix', 'apache']
```

**handlers/main.yml**:
```yaml
---
- name: Restart apache2
  ansible.builtin.service:
    name: "{{ poodle_fix_apache_service_name }}"
    state: restarted
  when: poodle_fix_restart_apache | bool

- name: Restart sshd
  ansible.builtin.service:
    name: sshd
    state: restarted
  when: poodle_fix_restart_sshd | bool
```

This migration plan addresses all modernization needs while preserving functionality and fixing the critical handler naming bug.