---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and fix handler naming inconsistencies.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate the POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

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

1. **SSL Configuration Update** (`poodle_fix.yml`):
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Changes the SSLProtocol directive to only allow TLSv1.2
   - Notifies handlers to restart Apache and SSH services
   - Legacy pattern: Short module name `replace:` instead of FQCN

2. **Service Restart Handlers** (`poodle_fix.yml`):
   - Contains handlers to restart Apache and SSH services
   - Uses the `ansible.builtin.service` module for Apache (modern FQCN)
   - Uses the `ansible.builtin.service` module for SSH (modern FQCN)
   - Handler name inconsistency: "Restart apache" vs "Restart apache2" in notification

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean syntax |
| Handler name inconsistency | Match handler name with notification | poodle_fix.yml | "Restart apache" vs "Restart apache2" |
| Playbook format | Role format | poodle_fix.yml | Convert from playbook to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the current role

## Checks for the Migration

**Files to verify**:
- tasks/main.yml (new file to create)
- handlers/main.yml (new file to create)
- meta/main.yml (new file to create)

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache SSL configuration: `apache2ctl -M | grep ssl`
- Check Apache SSL protocol settings: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Validate Apache configuration: `apache2ctl configtest`
- Verify SSH service status: `systemctl status sshd`
- Test SSL/TLS configuration: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify no SSLv3 support (POODLE mitigation): `openssl s_client -connect localhost:443 -ssl3` (should fail)