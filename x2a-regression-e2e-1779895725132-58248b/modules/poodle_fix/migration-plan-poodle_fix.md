---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This playbook mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The modernization needs include converting to FQCN module names, updating handler names for consistency, and restructuring into a proper role format.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate the POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**Task Files:**
- chef-and-ansible/poodle_fix.yml (currently a standalone playbook, not a role)

**Handler Files:**
- Handlers are embedded in the playbook (not in separate files)

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
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart Apache and SSH services
   - Legacy pattern: non-FQCN module name, handler name inconsistency

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name inconsistency (`Restart apache2` vs `Restart apache`) | Consistent handler naming | poodle_fix.yml | Handler name in notify doesn't match handler definition |
| Standalone playbook structure | Role structure with separate task/handler files | poodle_fix.yml | Convert to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required (uses only builtin modules)

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates present in the current implementation.

## Argument Specification

For meta/argument_specs.yml:
- No variables currently defined in the playbook

## Checks for the Migration

**Files to verify**:
- roles/poodle_fix/tasks/main.yml
- roles/poodle_fix/handlers/main.yml
- roles/poodle_fix/meta/main.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- None

## Pre-flight checks:
- Verify Apache configuration syntax: `apache2ctl configtest`
- Check SSL/TLS configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify SSH configuration: `sshd -t`
- Test for POODLE vulnerability: `nmap --script ssl-poodle -p 443 localhost`

## Migration Implementation Plan

1. **Create Role Directory Structure**:
   ```
   roles/
   └── poodle_fix/
       ├── tasks/
       │   └── main.yml
       ├── handlers/
       │   └── main.yml
       └── meta/
           └── main.yml
   ```

2. **Create tasks/main.yml**:
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
     author: Your Organization
     description: Role to mitigate POODLE vulnerability in Apache
     company: Your Company
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

5. **Example playbook.yml to use the role**:
   ```yaml
   ---
   - hosts: webservers
     become: true
     roles:
       - poodle_fix
   ```