---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for syntax updates, including fully qualified collection names (FQCN) for the replace module and handler notification consistency.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 for secure communications
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

```
poodle_fix.yml
```

**Task Files:**
poodle_fix.yml (contains inline tasks)

**Handler Files:**
poodle_fix.yml (contains inline handlers)

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

1. **Main tasks** (`poodle_fix.yml`):
   - Updates Apache SSL configuration to mitigate POODLE vulnerability by replacing the SSLProtocol directive
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart services after configuration change
   - Uses a handler name that doesn't match the handler definition ("Restart apache2" vs "Restart apache")

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | "Restart apache2" in notify vs "Restart apache" in handler definition |
| Playbook structure | Role structure | poodle_fix.yml | Convert from playbook to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required, uses only builtin modules

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache is already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the current playbook

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
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is running: `systemctl status sshd`
- Check Apache SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Validate Apache configuration: `apache2ctl configtest`
- Test SSL/TLS configuration: `nmap --script ssl-enum-ciphers -p 443 localhost`

## Migration Steps

1. **Create proper role directory structure**:
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
     notify:
       - Restart apache
       - Restart sshd
   ```

3. **Create handlers/main.yml**:
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

4. **Create meta/main.yml**:
   ```yaml
   ---
   galaxy_info:
     author: Your Name
     description: Role to fix POODLE vulnerability in Apache
     company: Your Company
     license: license (MIT, BSD)
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