---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on this file:

# Migration Plan: poodle_fix

**TLDR**: This playbook addresses the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The playbook needs modernization to use fully qualified collection names (FQCN), proper handler names, and should be restructured as a proper Ansible role.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to mitigate POODLE vulnerability
- Updates SSLProtocol directive to only allow TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The current implementation is a standalone playbook, not a proper role structure.**

Current file:
```
chef-and-ansible/poodle_fix.yml
```

Proposed role structure:
```
tasks/main.yml
handlers/main.yml
meta/main.yml
README.md
```

**Task Files:**
- tasks/main.yml (to be created)

**Handler Files:**
- handlers/main.yml (to be created)

**Variable Files:**
- defaults/main.yml (to be created)

**Meta:**
- meta/main.yml (to be created)

**Templates:**
None in the original playbook

**Static Files:**
None in the original playbook

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration Update** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Legacy pattern: Uses short module name `replace:` instead of FQCN
   - Modern equivalent: Use `ansible.builtin.replace:`
   - Ansible module mapping: `replace:` → `ansible.builtin.replace:`

2. **Service Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch (defined as "Restart apache" but notified as "Restart apache2")
   - Modern equivalent: Ensure handler names match notification names exactly

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names with notifications | poodle_fix.yml | "Restart apache" vs "Restart apache2" |
| Standalone playbook | Proper role structure | poodle_fix.yml | Convert to role structure |
| No role metadata | Create meta/main.yml | N/A | Add proper role metadata |
| No variable defaults | Create defaults/main.yml | N/A | Parameterize configuration |
| No documentation | Create README.md | N/A | Document role purpose and usage |

## Dependencies

**Collection dependencies** (for requirements.yml):
- No external collections required, only ansible.builtin

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache is already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates in the original playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: String, default: '/etc/apache2/mods-available/ssl.conf', Path to Apache SSL configuration file
- `ssl_protocol_setting`: String, default: '-all +TLSv1.2', SSL protocol settings to apply
- `restart_apache`: Boolean, default: true, Whether to restart Apache after configuration change
- `restart_ssh`: Boolean, default: true, Whether to restart SSH after configuration change

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- README.md

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Validate Apache configuration after changes: `apache2ctl configtest`
- Test SSL configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify POODLE vulnerability is mitigated: `nmap --script ssl-enum-ciphers -p 443 localhost`