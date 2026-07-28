---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and fix handler naming inconsistencies.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Updates Apache SSL configuration to mitigate the POODLE vulnerability by replacing the SSLProtocol line to only allow TLSv1.2
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart Apache and SSH services
   - Contains handler naming inconsistency: notifies "Restart apache2" but handler is named "Restart apache"
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean syntax |
| Handler name inconsistency | Match handler names with notifications | poodle_fix.yml | Handler "Restart apache" should be "Restart apache2" to match notification |
| Playbook structure | Convert to proper role structure | poodle_fix.yml | Convert from playbook to role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates present in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the current playbook that need to be included in argument specs.

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache configuration syntax: `apache2ctl configtest`
- Check SSL/TLS configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify SSH configuration: `sshd -t`
- Test that vulnerable protocols are disabled: `openssl s_client -connect localhost:443 -ssl3` (should fail)

## Conversion Plan from Playbook to Role

Since this is currently a playbook and not a role, here's how to convert it to a proper role structure:

1. Create the standard role directory structure:
   ```
   poodle_fix/
   ├── tasks/
   │   └── main.yml
   ├── handlers/
   │   └── main.yml
   ├── meta/
   │   └── main.yml
   └── README.md
   ```

2. Move the task from the playbook to `tasks/main.yml`:
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