---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper handler names, and structured playbook organization following current Ansible best practices.

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
   - Targets hosts in the 'myhost' group with root privileges
   - Updates Apache SSL configuration to disable vulnerable protocols and enable only TLSv1.2
   - Restarts Apache and SSH services after configuration changes
   - Legacy patterns found: short module name 'replace', handler name mismatch
   - Modern equivalent: Convert to proper role structure with FQCN modules

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler name with notify | poodle_fix.yml | Handler "Restart apache2" is notified but handler is named "Restart apache" |
| Standalone playbook | Structured role | poodle_fix.yml | Convert to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required for this simple role

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache is already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this playbook.

## Argument Specification

For meta/argument_specs.yml:
- No variables are defined in the current playbook

## Checks for the Migration

**Files to verify in the modern role**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- README.md

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache configuration syntax: `apache2ctl configtest`
- Check SSL/TLS configuration: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify SSH configuration: `sshd -t`
- Test for POODLE vulnerability: `openssl s_client -connect localhost:443 -ssl3` (should fail to connect)

## Migration Implementation Plan

To convert this standalone playbook into a proper Ansible role:

1. **Create role directory structure**:
   ```
   poodle_fix/
   ├── defaults/
   │   └── main.yml
   ├── handlers/
   │   └── main.yml
   ├── meta/
   │   └── main.yml
   ├── README.md
   └── tasks/
       └── main.yml
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
       - Restart apache2
       - Restart sshd
   ```

3. **handlers/main.yml**:
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

5. **README.md**:
   Create a comprehensive README with role description, requirements, variables, and usage examples.