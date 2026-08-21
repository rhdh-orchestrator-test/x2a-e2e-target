---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This role implements a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and to fix a handler name mismatch.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a structured Ansible role.**

poodle_fix.yml

## Module Explanation

The playbook performs operations in this order:

1. **poodle_fix.yml**:
   - Updates Apache SSL configuration to mitigate the POODLE vulnerability by replacing the SSLProtocol line to only allow TLSv1.2
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart Apache and SSH services
   - Contains a handler name mismatch ("Restart apache2" in notification vs "Restart apache" in handler definition)
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean syntax |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | "Restart apache2" notification doesn't match "Restart apache" handler |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None explicitly required

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are present in this playbook.

## Argument Specification

Since this is a standalone playbook rather than a role, argument specifications would be implemented differently. If converting to a role, the following variables could be defined:

- `poodle_fix_apache_config_path`: String, default: '/etc/apache2/mods-available/ssl.conf', path to Apache SSL configuration
- `poodle_fix_ssl_protocol`: String, default: '-all +TLSv1.2', SSL protocol configuration

## Checks for the Migration

**Files to verify**: 
- poodle_fix.yml (modernized)

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache configuration syntax: `apache2ctl configtest`
- Check SSL/TLS configuration: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify SSH configuration: `sshd -t`
- Test SSL/TLS security: `openssl s_client -connect localhost:443 -tls1_2`

## Migration Recommendations

1. **Convert to proper role structure**:
   - Create a directory structure with tasks/, handlers/, defaults/, and meta/ directories
   - Move tasks to tasks/main.yml
   - Move handlers to handlers/main.yml
   - Add defaults/main.yml with configurable variables
   - Add meta/main.yml with role metadata

2. **Fix handler name inconsistency**:
   - Either change the notification to "Restart apache" or the handler name to "Restart apache2"

3. **Add idempotency checks**:
   - Consider adding a check to verify if the configuration already matches before making changes

4. **Add more comprehensive SSL hardening**:
   - Consider adding cipher suite configurations
   - Add HSTS headers
   - Configure proper certificate settings