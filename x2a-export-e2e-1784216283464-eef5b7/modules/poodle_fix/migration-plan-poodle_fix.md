---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper handler names, and structured playbook organization.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a structured Ansible role.**

poodle_fix.yml

## Module Explanation

The playbook performs operations in this order:

1. **poodle_fix.yml**:
   - Updates Apache SSL configuration to mitigate POODLE vulnerability by replacing the SSLProtocol line
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart Apache and SSH services
   - Contains handlers directly in the playbook rather than in a separate handlers file
   - Has a handler name mismatch: notifies "Restart apache2" but handler is named "Restart apache"

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names exactly | poodle_fix.yml | "Restart apache2" notification vs "Restart apache" handler |
| Standalone playbook | Convert to role structure | poodle_fix.yml | Create proper role directory structure |
| No mode specified for file operations | Add `mode:` parameter | poodle_fix.yml | Ensure file permissions are explicitly set |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None
**Services managed**: apache2, sshd

## Template Modernization

No templates present in the current playbook.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the current playbook that need specification.

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
- Verify Apache configuration: `apache2ctl configtest`
- Check SSL/TLS configuration: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify SSH configuration: `sshd -t`
- Test SSL vulnerability: `openssl s_client -connect localhost:443 -ssl3`

## Migration Steps

1. **Create role directory structure**:
   ```
   mkdir -p poodle_fix/{tasks,handlers,meta}
   ```

2. **Create tasks/main.yml**:
   ```yaml
   ---
   - name: Fix SSL in Apache
     ansible.builtin.replace:
       dest: /etc/apache2/mods-available/ssl.conf
       regexp: '^SSLProtocol.*$'
       replace: 'SSLProtocol -all +TLSv1.2'
       mode: '0644'
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

4. **Create meta/main.yml**:
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