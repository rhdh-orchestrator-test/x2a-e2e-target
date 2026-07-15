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
- Enables only TLSv1.2 protocol for enhanced security
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a structured Ansible role.**

poodle_fix.yml

## Module Explanation

The playbook performs operations in this order:

1. **poodle_fix.yml**:
   - Targets hosts in the 'myhost' group with root privileges
   - Updates Apache SSL configuration to mitigate the POODLE vulnerability by replacing the SSLProtocol directive
   - Notifies handlers to restart Apache and SSH services after the configuration change
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | Handler "Restart apache2" is notified but defined as "Restart apache" |
| Missing mode parameter | Add `mode:` parameter | poodle_fix.yml | File operations should specify mode for security |
| Missing `changed_when` | Add condition for change detection | poodle_fix.yml | Improve idempotency reporting |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are present in this playbook.

## Argument Specification

As this is a standalone playbook rather than a role, argument specifications would be implemented differently. If converting to a role, the following variables could be defined:

- `poodle_fix_ssl_protocol`: string, default: '-all +TLSv1.2', description: "SSL protocols to enable/disable"
- `poodle_fix_apache_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: "Path to Apache SSL configuration file"

## Checks for the Migration

**Files to verify**: 
- poodle_fix.yml (modernized playbook)
- /etc/apache2/mods-available/ssl.conf (on target systems)

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Check current SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Validate Apache configuration after changes: `apache2ctl configtest`
- Test SSL/TLS configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify POODLE vulnerability is mitigated: `nmap --script ssl-enum-ciphers -p 443 localhost`

## Conversion to Role Structure

To convert this standalone playbook to a proper Ansible role, the following structure is recommended:

```
roles/poodle_fix/
├── defaults/
│   └── main.yml         # Default variables
├── handlers/
│   └── main.yml         # Handlers for service restarts
├── meta/
│   └── main.yml         # Role metadata
├── tasks/
│   └── main.yml         # Main tasks
└── README.md            # Role documentation
```

The task would be moved to tasks/main.yml, handlers to handlers/main.yml, and appropriate variables would be defined in defaults/main.yml.