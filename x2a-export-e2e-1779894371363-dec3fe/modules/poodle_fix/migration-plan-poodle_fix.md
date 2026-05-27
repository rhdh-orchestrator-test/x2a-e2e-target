---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This playbook mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The modernization needs include converting to FQCN module names, fixing handler names, and restructuring the playbook into a proper role format.

## Service Type and Configuration

**Service Type**: Web Server Security

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 to mitigate POODLE vulnerability
- Restarts Apache and SSH services after configuration changes

## File Structure

**Task Files:**
- chef-and-ansible/poodle_fix.yml (currently a standalone playbook, not a role)

**Handler Files:**
- Handlers are defined within the playbook (not in separate files)

**Variable Files:**
- None present

**Meta:**
- None present

**Templates:**
- None present

**Static Files:**
- None present

## Module Explanation

The playbook performs operations in this order:

1. **SSL Configuration Update** (`chef-and-ansible/poodle_fix.yml`):
   - Updates Apache SSL configuration to disable vulnerable protocols
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart services after changes
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Restart Handlers** (`chef-and-ansible/poodle_fix.yml`):
   - Defines handlers to restart Apache and SSH services
   - Handler name mismatch: Notifies "Restart apache2" but handler is named "Restart apache"
   - Uses `ansible.builtin.service` module (already modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names exactly | poodle_fix.yml | "Restart apache2" notification doesn't match "Restart apache" handler |
| Playbook structure | Role structure | poodle_fix.yml | Convert standalone playbook to proper role structure |
| No argument specs | Add meta/argument_specs.yml | N/A | Add argument specifications for role variables |

## Dependencies

**Collection dependencies** (for requirements.yml):
- No external collections required, only ansible.builtin

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache is already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates present in the current playbook.

## Argument Specification

For meta/argument_specs.yml:
- No variables currently used in the playbook

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache configuration: `apache2ctl configtest`
- Check SSL/TLS protocols: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify SSH configuration: `sshd -t`
- Check for open vulnerabilities: `openssl s_client -connect localhost:443 -tls1 -tlsextdebug`

## Migration Implementation Plan

1. **Create Role Directory Structure**:
   ```
   poodle_fix/
   ├── tasks/
   │   └── main.yml
   ├── handlers/
   │   └── main.yml
   ├── meta/
   │   ├── main.yml
   │   └── argument_specs.yml
   └── README.md
   ```

2. **tasks/main.yml**:
   ```yaml
   ---
   - name: Fix SSL in Apache
     ansible.builtin.replace:
       dest: /etc/apache2/mods-available/ssl.conf
       regexp: '^SSLProtocol.*$'
       replace: 'SSLProtocol -all +TLSv1.2'
     notify:
       - Restart apache
       - Restart sshd
   ```

3. **handlers/main.yml**:
   ```yaml
   ---
   - name: Restart apache
     ansible.builtin.service:
       name: apache2
       state: restarted

   - name: Restart sshd
     ansible.builtin.service:
       name: sshd
       state: restarted
   ```

4. **meta/main.yml**:
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

5. **meta/argument_specs.yml**:
   ```yaml
   ---
   argument_specs:
     main:
       short_description: Mitigates POODLE vulnerability in Apache SSL configuration
       description:
         - Updates Apache SSL configuration to disable vulnerable protocols
         - Enables only TLSv1.2 to mitigate POODLE vulnerability
       options: {}
   ```