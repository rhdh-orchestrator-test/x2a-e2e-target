---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for syntax updates, including fully qualified collection names (FQCN) for the replace module and handler notification consistency.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 for secure communications
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Updates the Apache SSL configuration file to mitigate the POODLE vulnerability by replacing the SSLProtocol directive
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Sets the SSL protocol to only allow TLSv1.2 and explicitly disable all other protocols
   - Notifies handlers to restart both Apache and SSH services after the change
   - Legacy patterns found: non-FQCN module name, handler name mismatch
   - Modern equivalent: Use FQCN for modules, ensure handler names match notifications

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names with notifications | poodle_fix.yml | Handler "Restart apache2" is notified but handler is named "Restart apache" |
| Missing `mode` parameter | Add `mode` parameter for file operations | poodle_fix.yml | Best practice for idempotency |
| Missing `backup` parameter | Consider adding `backup: true` | poodle_fix.yml | Best practice for safety |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

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
- meta/main.yml (to be created)
- meta/argument_specs.yml (to be created if variables are added)

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Check current SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- After applying role, verify configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Test SSL connection with: `openssl s_client -connect localhost:443 -tls1_2`
- Verify no SSLv3 support (POODLE mitigation): `openssl s_client -connect localhost:443 -ssl3` (should fail)