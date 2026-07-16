---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle-fix

**TLDR**: This role implements a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and fix handler naming inconsistencies.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate the POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a structured Ansible role.**

poodle_fix.yml

## Module Explanation

The playbook performs operations in this order:

1. **poodle_fix.yml**:
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Notifies handlers to restart Apache and SSH services after changes
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean syntax |
| Handler name mismatch | Match handler names with notifications | poodle_fix.yml | Handler "Restart apache2" is notified but handler is named "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are present in this playbook.

## Argument Specification

No variables are defined in this playbook that would require argument specifications.

## Checks for the Migration

**Files to verify**: 
- poodle_fix.yml (converted to role structure)

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache SSL configuration: `grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf`
- Test Apache configuration: `apache2ctl configtest`
- Verify Apache is running: `systemctl status apache2`
- Verify SSH is running: `systemctl status sshd`
- Test SSL/TLS configuration: `nmap --script ssl-enum-ciphers -p 443 localhost`

## Migration to Role Structure

Since the provided file is a standalone playbook rather than a role, here's how to convert it to a proper Ansible role structure:

1. Create the standard role directory structure:
   ```
   poodle_fix/
   ├── defaults/
   │   └── main.yml
   ├── handlers/
   │   └── main.yml
   ├── meta/
   │   └── main.yml
   ├── tasks/
   │   └── main.yml
   └── README.md
   ```

2. Move the tasks to `tasks/main.yml`:
   ```yaml
   ---
   - name: Fix SSL in Apache
     ansible.builtin.replace:
       dest: /etc/apache2/mods-available/ssl.conf
       regexp: '^SSLProtocol.*$'
       replace: 'SSLProtocol -all +TLSv1.2'
     notify:
       - Restart apache2
       - Restart sshd
   ```

3. Move the handlers to `handlers/main.yml`:
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

4. Create a basic `meta/main.yml`:
   ```yaml
   ---
   galaxy_info:
     role_name: poodle_fix
     author: your_name
     description: Fixes POODLE vulnerability in Apache SSL configuration
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

5. Create a basic `defaults/main.yml` for future extensibility:
   ```yaml
   ---
   # SSL protocol to enable
   ssl_protocol: "-all +TLSv1.2"
   
   # Path to Apache SSL config file
   apache_ssl_conf_path: /etc/apache2/mods-available/ssl.conf
   ```

6. Update `tasks/main.yml` to use variables:
   ```yaml
   ---
   - name: Fix SSL in Apache
     ansible.builtin.replace:
       dest: "{{ apache_ssl_conf_path }}"
       regexp: '^SSLProtocol.*$'
       replace: 'SSLProtocol {{ ssl_protocol }}'
     notify:
       - Restart apache2
       - Restart sshd
   ```