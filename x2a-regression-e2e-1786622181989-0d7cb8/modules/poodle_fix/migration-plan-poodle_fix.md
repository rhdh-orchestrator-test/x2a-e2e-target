---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper handler naming, and structured playbook organization.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

```
poodle_fix.yml
```

**Task Files:**
None (tasks are embedded in the playbook)

**Handler Files:**
None (handlers are embedded in the playbook)

**Variable Files:**
None

**Meta:**
None

**Templates:**
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **Main Playbook** (`poodle_fix.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Notifies handlers to restart Apache and SSH services
   - Legacy patterns found: short module name `replace`, handler name mismatch
   - Modern equivalent: Use FQCN `ansible.builtin.replace`, fix handler name consistency

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names in notify and handler definition | poodle_fix.yml | Handler "Restart apache2" in notify doesn't match "Restart apache" in handler definition |
| Playbook structure | Convert to role structure | poodle_fix.yml | Convert from standalone playbook to proper role structure |
| Missing `mode` parameter | Add `mode` parameter for file operations | poodle_fix.yml | Best practice for file operations |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

For meta/argument_specs.yml:
- `apache_ssl_config_path`: 
  - type: str
  - default: "/etc/apache2/mods-available/ssl.conf"
  - description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: 
  - type: str
  - default: "-all +TLSv1.2"
  - description: "SSL protocol configuration string"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
```
# Verify Apache configuration syntax
apache2ctl configtest

# Check SSL/TLS protocols enabled
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify SSH configuration
sshd -t

# Check services are running
systemctl status apache2
systemctl status sshd
```

## Migration Steps

1. Create proper role directory structure:
   ```
   mkdir -p poodle_fix/{tasks,handlers,defaults,meta}
   ```

2. Create tasks/main.yml:
   ```yaml
   ---
   - name: Fix SSL in Apache
     ansible.builtin.replace:
       dest: "{{ apache_ssl_config_path }}"
       regexp: '^SSLProtocol.*$'
       replace: 'SSLProtocol {{ ssl_protocol_setting }}'
       mode: '0644'
     notify:
       - Restart apache2
       - Restart sshd
   ```

3. Create handlers/main.yml:
   ```yaml
   ---
   - name: Restart apache2
     ansible.builtin.service:
       name: apache2
       state: restarted

   - name: Restart sshd
     ansible.builtin.service:
       name: sshd
       state: restarted
   ```

4. Create defaults/main.yml:
   ```yaml
   ---
   apache_ssl_config_path: /etc/apache2/mods-available/ssl.conf
   ssl_protocol_setting: "-all +TLSv1.2"
   ```

5. Create meta/main.yml:
   ```yaml
   ---
   galaxy_info:
     role_name: poodle_fix
     author: your_name
     description: Mitigates POODLE vulnerability in Apache SSL configuration
     license: MIT
     min_ansible_version: 2.9
     platforms:
       - name: Debian
         versions:
           - all
       - name: Ubuntu
         versions:
           - all
     galaxy_tags:
       - security
       - apache
       - ssl
       - poodle
   
   dependencies: []
   ```

6. Create meta/argument_specs.yml:
   ```yaml
   ---
   argument_specs:
     main:
       short_description: Role to mitigate POODLE vulnerability in Apache
       description:
         - Updates Apache SSL configuration to disable vulnerable protocols
         - Enables only TLSv1.2 to mitigate POODLE vulnerability
       options:
         apache_ssl_config_path:
           type: str
           default: /etc/apache2/mods-available/ssl.conf
           description: Path to Apache SSL configuration file
         ssl_protocol_setting:
           type: str
           default: "-all +TLSv1.2"
           description: SSL protocol configuration string
   ```