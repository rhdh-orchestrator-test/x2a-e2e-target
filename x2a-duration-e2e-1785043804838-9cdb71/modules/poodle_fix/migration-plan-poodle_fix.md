---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and fix handler naming inconsistencies.

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
   - Uses the `replace` module to modify Apache SSL configuration
   - Updates the SSLProtocol directive to disable all protocols except TLSv1.2
   - Notifies handlers to restart Apache and SSH services
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean syntax |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | Handler "Restart apache2" is notified but defined as "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required, uses only builtin modules

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this playbook.

## Argument Specification

For conversion to a proper role, the following variables should be defined in meta/argument_specs.yml:

- `apache_ssl_config_path`: String, default: '/etc/apache2/mods-available/ssl.conf', path to Apache SSL configuration
- `ssl_protocol_setting`: String, default: '-all +TLSv1.2', SSL protocol configuration string

## Checks for the Migration

**Files to verify**:
- tasks/main.yml (to be created)
- handlers/main.yml (to be created)
- defaults/main.yml (to be created)
- meta/main.yml (to be created)
- meta/argument_specs.yml (to be created)

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Check SSL configuration syntax: `apache2ctl configtest`
- Verify SSL protocol settings: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Test SSL connection with TLSv1.2: `openssl s_client -connect localhost:443 -tls1_2`
- Test SSL connection with older protocols (should fail): `openssl s_client -connect localhost:443 -tls1_1`

## Migration Recommendations

1. **Convert to proper role structure**:
   - Create standard role directories (tasks, handlers, defaults, meta)
   - Move task to tasks/main.yml
   - Move handlers to handlers/main.yml
   - Create defaults/main.yml with configurable variables
   - Create meta/main.yml with role metadata

2. **Fix handler naming inconsistency**:
   - Ensure handler name in notification matches the defined handler name

3. **Parameterize configuration**:
   - Make Apache config path configurable
   - Make SSL protocol setting configurable

4. **Add idempotency checks**:
   - Consider adding a check to verify if the change is needed before applying