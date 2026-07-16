---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This role implements a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for syntax updates, including fully qualified collection names (FQCN) for the replace module and handler notification consistency.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to mitigate the POODLE vulnerability
- Updates SSL protocol settings to disable all protocols except TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a structured Ansible role.**

poodle_fix.yml

## Module Explanation

The playbook performs operations in this order:

1. **poodle_fix.yml**:
   - Targets hosts in the 'myhost' group with root privileges
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the replace module to modify /etc/apache2/mods-available/ssl.conf
   - Notifies handlers to restart Apache and SSH services after changes
   - Legacy patterns found: non-FQCN module names, handler name mismatch
   - Modern equivalent: Use FQCN for modules, ensure handler names match notifications

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names with notifications | poodle_fix.yml | Handler "Restart apache2" is notified but handler is named "Restart apache" |
| Inconsistent indentation | Consistent indentation (2 spaces) | poodle_fix.yml | Formatting |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are present in this standalone playbook.

## Argument Specification

Since this is a standalone playbook rather than a role, argument specifications would not apply in the traditional sense. If converting to a role, variables to consider would be:
- apache_ssl_config_path: Path to Apache SSL configuration file
- ssl_protocol_setting: The specific SSL protocol configuration to apply

## Checks for the Migration

**Files to verify**: 
- poodle_fix.yml (modernized playbook)

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Check current SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- After applying, verify SSL settings: `apache2ctl -t -D DUMP_MODULES | grep ssl`
- Test SSL connection security: `openssl s_client -connect localhost:443 -tls1_2`

## Recommended Role Structure Conversion

To convert this standalone playbook to a proper Ansible role, the following structure is recommended:

```
roles/poodle_fix/
├── defaults/
│   └── main.yml         # Default variables
├── handlers/
│   └── main.yml         # Handler definitions
├── meta/
│   └── main.yml         # Role metadata
├── tasks/
│   └── main.yml         # Task definitions
└── README.md            # Role documentation
```

The task file would contain the SSL configuration update, and the handlers file would contain the service restart handlers. This would make the security fix more reusable and maintainable.