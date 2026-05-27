---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This playbook mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The modernization needs include converting to a proper role structure, using FQCN for modules, fixing handler names, and implementing proper boolean syntax.

## Service Type and Configuration

**Service Type**: Web Server Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**Task Files:**
- chef-and-ansible/poodle_fix.yml (currently a standalone playbook, not a role)

**Handler Files:**
- Handlers are defined within the playbook (not in separate files)

**Variable Files:**
- None present

**Meta:**
- None present

**Templates:**
- None present

**Static Files:**
- None present

## Module Explanation

The playbook performs operations in this order:

1. **SSL Configuration Update** (`chef-and-ansible/poodle_fix.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module without FQCN
   - Notifies two handlers: "Restart apache2" and "Restart sshd", but the first handler is named "Restart apache" (name mismatch)
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Handlers** (`chef-and-ansible/poodle_fix.yml`):
   - Two handlers defined: "Restart apache" and "Restart sshd"
   - "Restart apache" uses FQCN `ansible.builtin.service` but "Restart sshd" doesn't
   - Handler name mismatch: task notifies "Restart apache2" but handler is named "Restart apache"
   - Ansible module mapping: `service` → `ansible.builtin.service`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `service:` | `ansible.builtin.service:` | poodle_fix.yml | FQCN (already used in one handler) |
| Handler name mismatch | Fix handler name to match notification | poodle_fix.yml | Task notifies "Restart apache2" but handler is "Restart apache" |
| Standalone playbook | Convert to proper role structure | poodle_fix.yml | Create role directory structure |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean syntax |

## Dependencies

**Collection dependencies** (for requirements.yml):
- No external collections required

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache is already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates present in the current implementation.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the current implementation, but could add:
  - `ssl_protocol`: string, default: '-all +TLSv1.2', description: "SSL protocols to enable/disable"
  - `apache_conf_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: "Path to Apache SSL configuration file"

## Checks for the Migration

**Files to verify**:
- roles/poodle_fix/tasks/main.yml
- roles/poodle_fix/handlers/main.yml
- roles/poodle_fix/meta/main.yml
- roles/poodle_fix/meta/argument_specs.yml
- roles/poodle_fix/defaults/main.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache configuration syntax: `apache2ctl configtest`
- Verify SSH configuration syntax: `sshd -t`
- Check SSL/TLS configuration: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify no SSLv3 support (POODLE mitigation): `openssl s_client -connect localhost:443 -ssl3`