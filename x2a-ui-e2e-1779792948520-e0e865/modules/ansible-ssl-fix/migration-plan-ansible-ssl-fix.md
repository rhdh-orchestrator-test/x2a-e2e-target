---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: ansible-ssl-fix

**TLDR**: This role configures Apache and SSH servers to mitigate the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2. The modernization needs include converting to FQCN module names, proper handler naming, and restructuring into a proper Ansible role format.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Ensures only TLSv1.2 is enabled in Apache
- Restarts Apache and SSH services after configuration changes

## File Structure

**Task Files:**
- chef-and-ansible/poodle_fix.yml (currently a playbook, not a proper role structure)

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

The role performs operations in this order:

1. **SSL Configuration Fix** (`chef-and-ansible/poodle_fix.yml`):
   - Modifies the Apache SSL configuration file to disable vulnerable SSL protocols
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart Apache and SSH services
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Handlers** (`chef-and-ansible/poodle_fix.yml`):
   - Contains handlers to restart Apache and SSH services
   - Handler name mismatch: "Restart apache" vs "Restart apache2" in notification
   - Uses `ansible.builtin.service` module (already modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent handler naming | poodle_fix.yml | "Restart apache" vs "Restart apache2" in notification |
| Playbook structure | Role structure | poodle_fix.yml | Convert to proper role structure |
| Missing mode parameter | Add `mode:` parameter | poodle_fix.yml | File permissions not specified for file operations |
| Missing `changed_when` | Add conditional for change detection | poodle_fix.yml | Improve idempotency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- No external collections required

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates present in the current implementation.

## Argument Specification

For meta/argument_specs.yml:
- `apache_ssl_config_path`: 
  - type: str
  - default: "/etc/apache2/mods-available/ssl.conf"
  - description: "Path to Apache SSL configuration file"
- `ssl_protocol_string`: 
  - type: str
  - default: "-all +TLSv1.2"
  - description: "SSL protocol string to configure in Apache"

## Checks for the Migration

**Files to verify**:
- roles/ansible-ssl-fix/tasks/main.yml
- roles/ansible-ssl-fix/handlers/main.yml
- roles/ansible-ssl-fix/defaults/main.yml
- roles/ansible-ssl-fix/meta/main.yml
- roles/ansible-ssl-fix/meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Check current SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Validate Apache configuration after changes: `apache2ctl configtest`
- Test SSL/TLS configuration: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify POODLE vulnerability is mitigated: `openssl s_client -connect localhost:443 -ssl3` (should fail)