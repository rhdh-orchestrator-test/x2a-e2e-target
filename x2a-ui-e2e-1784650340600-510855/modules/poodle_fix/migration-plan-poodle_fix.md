---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for syntax updates, including fully qualified collection names (FQCN) for the replace module and handler naming consistency.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Updates the Apache SSL configuration file to mitigate the POODLE vulnerability by replacing the SSLProtocol line with one that only allows TLSv1.2
   - Uses the `replace` module without FQCN
   - Notifies two handlers: "Restart apache2" and "Restart sshd", but the first handler is named "Restart apache" in the handlers section (naming inconsistency)
   - The handlers use the `ansible.builtin.service` module (already using FQCN)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch: "Restart apache2" in notify vs "Restart apache" in handler definition | Use consistent handler name: "Restart apache2" | poodle_fix.yml | Handler naming consistency |
| Playbook structure | Convert to role structure | poodle_fix.yml | Convert standalone playbook to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables are defined in the current playbook, but the following could be added for flexibility:
  - `apache_ssl_config_path`: String, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'
  - `ssl_protocol_setting`: String, default: '-all +TLSv1.2', description: 'SSL protocol settings for Apache'

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- meta/argument_specs.yml
- defaults/main.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Check SSL configuration syntax: `apache2ctl configtest`
- Verify SSL settings after applying: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Test SSL connection with: `openssl s_client -connect localhost:443 -tls1_2`
- Verify no SSLv3 support (POODLE mitigation): `openssl s_client -connect localhost:443 -ssl3` (should fail)

## Migration Steps

1. **Create proper role structure**:
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
       replace: "SSLProtocol {{ ssl_protocol_setting }}"
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
   ssl_protocol_setting: -all +TLSv1.2
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
       short_description: Role to mitigate POODLE vulnerability in Apache
       description:
         - This role updates Apache SSL configuration to disable vulnerable SSL protocols
         - and enable only TLSv1.2 to mitigate the POODLE vulnerability
       options:
         apache_ssl_config_path:
           type: str
           default: /etc/apache2/mods-available/ssl.conf
           description: Path to Apache SSL configuration file
         ssl_protocol_setting:
           type: str
           default: "-all +TLSv1.2"
           description: SSL protocol settings for Apache
   ```