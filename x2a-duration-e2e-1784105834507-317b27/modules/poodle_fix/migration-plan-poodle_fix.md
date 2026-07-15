---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for syntax updates, including fully qualified collection names (FQCN) for the replace module and fixing a handler name mismatch.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to mitigate the POODLE vulnerability
- Updates the SSLProtocol directive to disable all protocols except TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Connects to target hosts as root with privilege escalation
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols
   - Uses the replace module to modify the SSLProtocol directive
   - Notifies handlers to restart Apache and SSH services after changes
   - Contains a handler name mismatch ("Restart apache2" in notify vs "Restart apache" in handler definition)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Fix handler name consistency | poodle_fix.yml | "Restart apache2" in notify vs "Restart apache" in handler |
| Playbook structure | Convert to role structure | poodle_fix.yml | Convert standalone playbook to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are present in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables are defined in the current playbook, but the following could be added for flexibility:
  - `ssl_config_path`: String, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'
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
- Validate Apache configuration after changes: `apache2ctl configtest`
- Check SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Verify TLS version with: `nmap --script ssl-enum-ciphers -p 443 localhost`

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
       dest: "{{ ssl_config_path }}"
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
   ssl_config_path: /etc/apache2/mods-available/ssl.conf
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
       short_description: Role to fix POODLE vulnerability in Apache
       description: Updates Apache SSL configuration to disable vulnerable protocols
       options:
         ssl_config_path:
           type: str
           default: /etc/apache2/mods-available/ssl.conf
           description: Path to Apache SSL configuration file
         ssl_protocol_setting:
           type: str
           default: "-all +TLSv1.2"
           description: SSL protocol settings for Apache
   ```