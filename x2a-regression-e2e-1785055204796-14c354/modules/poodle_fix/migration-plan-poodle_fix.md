---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and fix handler naming inconsistencies.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables all SSL protocols except TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a structured Ansible role.**

poodle_fix.yml

## Module Explanation

The playbook performs operations in this order:

1. **poodle_fix.yml**:
   - Targets hosts in the 'myhost' group with root privileges
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Notifies handlers to restart Apache and SSH services
   - Contains handlers for restarting Apache and SSH services
   - Legacy patterns found: non-FQCN module names, handler name inconsistency
   - Modern equivalent: Use FQCN for all modules, ensure handler names match notification names

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name inconsistency | Match handler names with notify names | poodle_fix.yml | Handler "Restart apache" vs notify "Restart apache2" |
| Playbook structure | Convert to role structure | poodle_fix.yml | Convert standalone playbook to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required, uses only builtin modules

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are present in this playbook.

## Argument Specification

For the role conversion, the following variables should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: String, default: '/etc/apache2/mods-available/ssl.conf', description: "Path to Apache SSL configuration file"
- `ssl_protocol_string`: String, default: '-all +TLSv1.2', description: "SSL protocol configuration string"

## Checks for the Migration

**Files to verify in the new role structure**:
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
```bash
# Verify Apache SSL configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify Apache is running with new configuration
systemctl status apache2

# Verify SSH is running
systemctl status sshd

# Test SSL/TLS configuration
nmap --script ssl-enum-ciphers -p 443 localhost
```

## Migration Steps

1. **Create role directory structure**:
   ```
   mkdir -p poodle_fix/{tasks,handlers,defaults,meta}
   ```

2. **Create tasks/main.yml**:
   ```yaml
   ---
   - name: Fix SSL in Apache
     ansible.builtin.replace:
       dest: "{{ apache_ssl_config_path }}"
       regexp: '^SSLProtocol.*$'
       replace: "SSLProtocol {{ ssl_protocol_string }}"
     notify:
       - Restart apache2
       - Restart sshd
   ```

3. **Create handlers/main.yml**:
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

4. **Create defaults/main.yml**:
   ```yaml
   ---
   apache_ssl_config_path: /etc/apache2/mods-available/ssl.conf
   ssl_protocol_string: "-all +TLSv1.2"
   ```

5. **Create meta/main.yml**:
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

6. **Create meta/argument_specs.yml**:
   ```yaml
   ---
   argument_specs:
     main:
       short_description: Mitigates POODLE vulnerability in Apache SSL configuration
       description:
         - Updates Apache SSL configuration to disable vulnerable protocols
         - Enables only TLSv1.2 to mitigate POODLE vulnerability
       options:
         apache_ssl_config_path:
           type: str
           default: /etc/apache2/mods-available/ssl.conf
           description: Path to Apache SSL configuration file
         ssl_protocol_string:
           type: str
           default: "-all +TLSv1.2"
           description: SSL protocol configuration string
   ```