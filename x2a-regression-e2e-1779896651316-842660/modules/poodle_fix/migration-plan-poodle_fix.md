---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This playbook mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The modernization needs include converting to FQCN module names, fixing handler names, and restructuring into a proper role format.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**Task Files:**
- chef-and-ansible/poodle_fix.yml (standalone playbook, not a proper role structure)

**Handler Files:**
- Handlers are defined within the playbook itself

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
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart services after configuration change
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Restart Handlers** (`chef-and-ansible/poodle_fix.yml`):
   - Contains handlers to restart Apache and SSH services
   - Handler name mismatch: Notifies "Restart apache2" but handler is named "Restart apache"
   - Uses `ansible.builtin.service` module (already using FQCN)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names exactly | poodle_fix.yml | "Restart apache2" notification doesn't match "Restart apache" handler |
| Standalone playbook | Convert to proper role structure | poodle_fix.yml | Create tasks/main.yml, handlers/main.yml, etc. |
| No argument specs | Add meta/argument_specs.yml | N/A | Define role parameters |
| No role metadata | Add meta/main.yml | N/A | Define role metadata |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required, only uses builtin modules

**Role dependencies**: None
**External packages**: None explicitly installed
**Services managed**: apache2, sshd

## Template Modernization

No templates present in the current implementation.

## Argument Specification

For meta/argument_specs.yml:
- `apache_ssl_config_path`: 
  - Type: string
  - Default: "/etc/apache2/mods-available/ssl.conf"
  - Description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: 
  - Type: string
  - Default: "-all +TLSv1.2"
  - Description: "SSL protocol configuration string"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache configuration syntax
apache2ctl configtest

# Check SSL/TLS configuration
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify SSH configuration
sshd -t

# Test for POODLE vulnerability
openssl s_client -connect localhost:443 -ssl3
# Should fail with "wrong version number" if SSLv3 is disabled
```

## Proposed Role Structure

The standalone playbook should be converted to a proper role with this structure:

```
poodle_fix/
├── defaults/
│   └── main.yml         # Default variables
├── handlers/
│   └── main.yml         # Service restart handlers
├── meta/
│   ├── main.yml         # Role metadata
│   └── argument_specs.yml  # Role argument specifications
├── README.md            # Role documentation
└── tasks/
    └── main.yml         # SSL configuration tasks
```