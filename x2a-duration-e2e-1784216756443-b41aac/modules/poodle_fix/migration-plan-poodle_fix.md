---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and fix handler naming inconsistencies.

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
   - Targets hosts in the 'myhost' group with root privileges
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols and enable only TLSv1.2
   - Notifies handlers to restart Apache and SSH services after configuration changes
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean syntax |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | Handler "Restart apache2" is notified but handler is named "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- No external collections required, only ansible.builtin modules

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables are defined in this playbook that would require argument specifications

## Checks for the Migration

**Files to verify**: 
- poodle_fix.yml (modernized)

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Verify SSL module is enabled in Apache: `apache2ctl -M | grep ssl`
- Check SSL configuration file exists: `ls -la /etc/apache2/mods-available/ssl.conf`
- Validate Apache configuration after changes: `apache2ctl configtest`
- Test SSL configuration with: `openssl s_client -connect localhost:443 -tls1_2`
- Verify no vulnerable protocols are enabled: `nmap --script ssl-enum-ciphers -p 443 localhost`