---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a traditional Ansible role structure. Let me provide the migration specification:

# Migration Plan: poodle-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by updating Apache SSL configuration to disable vulnerable protocols and enforce TLS 1.2. The main modernization needs include converting from playbook to role structure, fixing FQCN usage, correcting handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration in Apache
- Disables vulnerable SSL protocols (-all)
- Enforces TLS 1.2 only (+TLSv1.2)
- Restarts Apache and SSH services to apply changes

## File Structure

**Current Structure (Playbook):**
```
poodle_fix.yml
```

**Target Role Structure:**
```
tasks/main.yml
handlers/main.yml
defaults/main.yml
meta/main.yml
meta/argument_specs.yml
```

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - Uses `replace` module to update Apache SSL configuration
   - Targets `/etc/apache2/mods-available/ssl.conf`
   - Replaces any existing `SSLProtocol` directive with `SSLProtocol -all +TLSv1.2`
   - Notifies handlers to restart services
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Restart Handlers**:
   - Handler naming inconsistency: notifies "Restart apache2" but handler named "Restart apache"
   - Restarts both Apache and SSH services
   - Uses modern FQCN `ansible.builtin.service` (already modernized)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Fix notification names | tasks/main.yml, handlers/main.yml | "Restart apache2" → "Restart apache" |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| Hard-coded paths | Variables | tasks/main.yml | `/etc/apache2/mods-available/ssl.conf` → variable |
| Missing argument specs | Add meta/argument_specs.yml | New file | Role validation |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: Apache2 (assumed pre-installed)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates present in current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_services`: list, default: ["apache2", "sshd"], description: "Services to restart after SSL configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted from playbook)
- handlers/main.yml (extracted handlers)
- defaults/main.yml (new variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (argument validation)

**Services to check**: 
- apache2 (SSL configuration applied)
- sshd (service restarted successfully)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest

# Check SSL protocol configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify services are running
systemctl status apache2
systemctl status sshd

# Test SSL configuration (if applicable)
openssl s_client -connect localhost:443 -tls1_2

# Verify POODLE vulnerability is fixed
nmap --script ssl-poodle localhost -p 443
```

**Critical Migration Notes:**
1. **Handler Name Fix**: The current playbook has a mismatch where it notifies "Restart apache2" but the handler is named "Restart apache". This must be corrected.
2. **Playbook to Role Conversion**: This is currently a standalone playbook that needs to be restructured as a proper Ansible role.
3. **Variable Extraction**: Hard-coded paths and configurations should be extracted to variables for flexibility.
4. **FQCN Compliance**: The `replace` module needs to be updated to `ansible.builtin.replace`.
5. **Boolean Modernization**: `become: yes` should be `become: true`.
6. **Security Validation**: Add tasks to validate the SSL configuration change was successful before considering the role complete.