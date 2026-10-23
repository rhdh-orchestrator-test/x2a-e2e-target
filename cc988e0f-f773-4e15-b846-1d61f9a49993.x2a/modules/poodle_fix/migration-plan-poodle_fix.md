---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a **playbook**, not a role. However, I'll provide a migration specification to convert this legacy playbook into a modern Ansible role structure. Let me provide the detailed migration plan:

---

# Migration Plan: poodle_fix

**TLDR**: This is a legacy playbook (not a role) that fixes the POODLE SSL vulnerability by configuring Apache to use only TLSv1.2 protocol. It needs to be converted into a proper role structure and modernized with FQCN module names, proper handler naming consistency, and role-based organization following current best practices.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Applies POODLE vulnerability fix to Apache SSL configuration
- Modifies `/etc/apache2/mods-available/ssl.conf` to enforce TLSv1.2 only
- Restarts Apache2 service to apply changes
- Restarts SSHD service (handler defined but logic seems incorrect - notified but unrelated to Apache SSL config)
- Uses regex replacement for SSL protocol configuration

## File Structure

**Current Structure (Playbook):**
```
poodle_fix.yml
```

**Target Structure (Role):**
```
roles/poodle_fix/tasks/main.yml
roles/poodle_fix/handlers/main.yml
roles/poodle_fix/defaults/main.yml
roles/poodle_fix/meta/main.yml
roles/poodle_fix/meta/argument_specs.yml
roles/poodle_fix/README.md
```

**Additional Metadata (for Collection/EE):**
```
roles/poodle_fix/execution-environment.yml
roles/poodle_fix/bindep.txt
collections/requirements.yml
```

## Module Explanation

The playbook performs operations in this order:

1. **Fix SSL in Apache** (`poodle_fix.yml` - task section):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration file
   - **Step 2**: Legacy patterns found:
     - Missing FQCN: `replace:` should be `ansible.builtin.replace:`
     - Inline parameters instead of structured format
     - Privilege escalation at play level (`become: yes` should be `become: true`)
     - Handler naming inconsistency: notifies "Restart apache2" but handler is named "Restart apache"
     - Questionable logic: notifies both Apache and SSHD restart for Apache SSL config change
   - **Step 3**: Modern equivalent:
     - Use FQCN `ansible.builtin.replace:`
     - Use structured YAML with proper indentation
     - Use boolean `true` instead of `yes`
     - Fix handler naming consistency
     - Remove SSHD restart notification (unrelated to Apache SSL)
     - Add `mode:` parameter to ensure file permissions are explicitly set
     - Add variables for configurable paths and SSL protocols
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Handlers** (`poodle_fix.yml` - handlers section):
   - **Step 1**: Defines service restart handlers
   - **Step 2**: Legacy patterns found:
     - Handler name mismatch: task notifies "Restart apache2" but handler is "Restart apache"
     - One handler already uses FQCN (`ansible.builtin.service`), the other doesn't
     - SSHD restart handler appears unrelated to POODLE/Apache fix
   - **Step 3**: Modern equivalent:
     - Fix handler naming to match notifications
     - Ensure both handlers use FQCN
     - Consider removing SSHD handler or documenting why it's needed
     - Move handlers to separate handlers/main.yml file
   - Ansible module mapping: Both handlers correctly use `ansible.builtin.service` (already modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN required |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean modernization |
| Inline module params | Structured YAML dict | poodle_fix.yml | Readability and maintainability |
| Handler name mismatch | Consistent naming | poodle_fix.yml | "Restart apache2" notify → "Restart apache" handler |
| Playbook structure | Role structure | poodle_fix.yml | Convert to proper role layout |
| Hardcoded paths | Variables in defaults | poodle_fix.yml | `/etc/apache2/mods-available/ssl.conf` → `apache_ssl_conf_path` |
| Hardcoded protocol | Variables in defaults | poodle_fix.yml | `TLSv1.2` → `apache_ssl_protocols` |
| Missing file mode | Add `mode:` parameter | poodle_fix.yml | Explicit file permissions |
| No backup option | Add `backup: true` | poodle_fix.yml | Safety for config changes |
| Bare remote_user/hosts | Role variables | poodle_fix.yml | Move to play-level or inventory |

## Dependencies

**Collection dependencies** (for collections/requirements.yml):
```yaml
collections:
  - name: ansible.builtin
    version: ">=2.10"
```

**Role dependencies**: None (standalone security hardening role)

**External packages**: 
- Apache2 (assumes already installed)
- OpenSSH server (assumes already installed)

**Services managed**: 
- apache2 (restarted after configuration change)
- sshd (currently notified but questionable - should be reviewed)

## Template Modernization

No Jinja2 templates in the original playbook. Consider adding:
- **ssl.conf.j2**: Template for complete Apache SSL configuration (more maintainable than regex replacement)

## Argument Specification

Document variables for `meta/argument_specs.yml`:

```yaml
argument_specs:
  main:
    short_description: POODLE vulnerability fix for Apache SSL configuration
    description:
      - Configures Apache to use secure SSL/TLS protocols only
      - Mitigates POODLE vulnerability by disabling SSLv3 and older protocols
    options:
      apache_ssl_conf_path:
        type: path
        required: false
        default: /etc/apache2/mods-available/ssl.conf
        description: Path to Apache SSL configuration file
      
      apache_ssl_protocols:
        type: str
        required: false
        default: "-all +TLSv1.2 +TLSv1.3"
        description: SSL/TLS protocols to enable (updated to include TLSv1.3)
      
      apache_service_name:
        type: str
        required: false
        default: apache2
        description: Name of the Apache service
      
      apache_backup_config:
        type: bool
        required: false
        default: true
        description: Whether to backup configuration file before modification
      
      apache_restart_required:
        type: bool
        required: false
        default: true
        description: Whether to restart Apache after configuration change
```

## Checks for the Migration

**Files to verify**: 
- roles/poodle_fix/tasks/main.yml
- roles/poodle_fix/handlers/main.yml
- roles/poodle_fix/defaults/main.yml
- roles/poodle_fix/meta/main.yml
- roles/poodle_fix/meta/argument_specs.yml
- roles/poodle_fix/README.md

**Services to check**: 
- apache2 (primary service)
- sshd (review if restart is actually needed)

**Templates to validate**: 
- None in original; consider creating ssl.conf.j2 for better maintainability

## Pre-flight checks:

**Before applying the role:**
```bash
# Verify Apache is installed and SSL module exists
ansible target_hosts -m ansible.builtin.command -a "apache2 -v"
ansible target_hosts -m ansible.builtin.stat -a "path=/etc/apache2/mods-available/ssl.conf"

# Backup current configuration
ansible target_hosts -m ansible.builtin.copy -a "src=/etc/apache2/mods-available/ssl.conf dest=/etc/apache2/mods-available/ssl.conf.backup remote_src=yes"

# Check current SSL configuration
ansible target_hosts -m ansible.builtin.command -a "grep SSLProtocol /etc/apache2/mods-available/ssl.conf"
```

**After applying the role:**
```bash
# Verify Apache configuration syntax
ansible target_hosts -m ansible.builtin.command -a "apache2ctl configtest"

# Verify Apache is running
ansible target_hosts -m ansible.builtin.service -a "name=apache2 state=started"

# Verify SSL protocol configuration
ansible target_hosts -m ansible.builtin.command -a "grep SSLProtocol /etc/apache2/mods-available/ssl.conf"

# Test SSL/TLS protocols using openssl (should fail for SSLv3, succeed for TLSv1.2+)
# Run from control node:
openssl s_client -connect target_host:443 -ssl3  # Should fail
openssl s_client -connect target_host:443 -tls1_2  # Should succeed

# Verify with nmap
nmap --script ssl-enum-ciphers -p 443 target_host
```

## Additional Recommendations

1. **Handler Logic Review**: The current playbook notifies both "Restart apache2" and "Restart sshd" handlers when Apache SSL config changes. The SSHD restart appears unrelated to the POODLE fix for Apache. Review if this is intentional or should be removed.

2. **Security Enhancement**: Consider updating the SSL protocol configuration from only `TLSv1.2` to `TLSv1.2 +TLSv1.3` to include TLS 1.3 support (if Apache version supports it).

3. **Idempotency**: The `replace` module is idempotent by default, but consider adding a validation task to check if the configuration is already correct before making changes.

4. **Platform Support**: The current implementation assumes Debian/Ubuntu (apache2 package/service name). Consider adding support for RHEL/CentOS (httpd) using variables or conditionals.

5. **Validation Task**: Add a task to validate Apache configuration (`apache2ctl configtest`) before restarting the service to prevent service disruption from invalid configuration.

6. **Complete SSL Hardening**: The POODLE fix only addresses SSL protocols. Consider expanding to a comprehensive SSL hardening role that also addresses:
   - Cipher suite configuration
   - SSL certificate management
   - HSTS headers
   - SSL session configuration

## Modern Role Structure Example

**roles/poodle_fix/tasks/main.yml:**
```yaml
---
- name: Ensure Apache SSL configuration directory exists
  ansible.builtin.stat:
    path: "{{ apache_ssl_conf_path | dirname }}"
  register: apache_ssl_dir
  check_mode: false

- name: Fail if Apache SSL configuration directory does not exist
  ansible.builtin.fail:
    msg: "Apache SSL configuration directory does not exist: {{ apache_ssl_conf_path | dirname }}"
  when: not apache_ssl_dir.stat.exists

- name: Fix POODLE vulnerability in Apache SSL configuration
  ansible.builtin.replace:
    path: "{{ apache_ssl_conf_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "SSLProtocol {{ apache_ssl_protocols }}"
    backup: "{{ apache_backup_config }}"
    validate: 'apache2ctl -t -f %s'
  notify: restart apache2
  when: apache_restart_required | bool
```

**roles/poodle_fix/handlers/main.yml:**
```yaml
---
- name: restart apache2
  ansible.builtin.service:
    name: "{{ apache_service_name }}"
    state: restarted
```

**roles/poodle_fix/defaults/main.yml:**
```yaml
---
# Apache SSL configuration file path
apache_ssl_conf_path: /etc/apache2/mods-available/ssl.conf

# SSL/TLS protocols to enable (POODLE fix)
apache_ssl_protocols: "-all +TLSv1.2 +TLSv1.3"

# Apache service name (apache2 for Debian/Ubuntu, httpd for RHEL/CentOS)
apache_service_name: apache2

# Backup configuration before changes
apache_backup_config: true

# Restart Apache after configuration change
apache_restart_required: true
```

**roles/poodle_fix/meta/main.yml:**
```yaml
---
galaxy_info:
  role_name: poodle_fix
  author: Your Organization
  description: POODLE vulnerability fix for Apache SSL configuration
  license: MIT
  min_ansible_version: "2.10"
  platforms:
    - name: Debian
      versions:
        - buster
        - bullseye
    - name: Ubuntu
      versions:
        - focal
        - jammy
  galaxy_tags:
    - security
    - apache
    - ssl
    - poodle
    - vulnerability

dependencies: []
```

This migration plan provides a complete path from the legacy playbook to a modern, reusable, and maintainable Ansible role following current best practices.