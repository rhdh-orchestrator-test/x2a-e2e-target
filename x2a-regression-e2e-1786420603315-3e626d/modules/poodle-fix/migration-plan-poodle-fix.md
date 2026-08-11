---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle-fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and only allow TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and fix handler naming inconsistencies.

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
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and only enable TLSv1.2
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Notifies handlers to restart Apache and SSH services after configuration changes
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean syntax |
| Handler name mismatch | Fix handler name consistency | poodle_fix.yml | Handler "Restart apache2" is notified but defined as "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required (uses only builtin modules)

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this playbook.

## Argument Specification

Since this is a standalone playbook and not a role, no argument specification is needed.

## Checks for the Migration

**Files to verify**: 
- poodle_fix.yml (modernized playbook)

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Check Apache syntax: `apache2ctl configtest`
- Verify Apache is running with updated configuration: `systemctl status apache2`
- Verify SSH is running: `systemctl status sshd`
- Test SSL/TLS configuration: `nmap --script ssl-enum-ciphers -p 443 localhost`

## Migration Recommendations

1. **Convert to proper role structure**:
   - Create a standard role directory structure with tasks, handlers, defaults, etc.
   - Move the task to tasks/main.yml
   - Move handlers to handlers/main.yml

2. **Fix handler name inconsistency**:
   - Either change the notify to "Restart apache" or rename the handler to "Restart apache2"

3. **Add proper documentation**:
   - Create README.md explaining the role's purpose and usage
   - Document variables and their defaults

4. **Add idempotency checks**:
   - Consider adding a check to verify if the configuration already matches before making changes

5. **Add variable support**:
   - Make the SSL protocol configuration a variable that can be customized