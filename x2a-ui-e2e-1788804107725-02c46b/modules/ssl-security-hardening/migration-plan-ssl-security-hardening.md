---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a traditional Ansible role structure. However, I can still provide a migration plan to modernize this into a proper Ansible role following current best practices.

# Migration Plan: SSL Security Hardening (POODLE Fix)

**TLDR**: This is a single-task playbook that hardens Apache SSL configuration by disabling vulnerable SSL protocols and enforcing TLS 1.2 to mitigate the POODLE vulnerability. Key modernization needs include converting from playbook to role structure, updating module syntax to use FQCN, fixing handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enforces TLS 1.2 only protocol usage
- Restarts Apache2 and SSH services after configuration changes
- Mitigates POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability

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

1. **SSL Protocol Hardening** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, handler naming mismatch
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper handler references
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent handler naming | handlers/main.yml | "Restart apache" vs "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Hardcoded paths | Parameterized variables | tasks/main.yml | Make paths configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by system)
**Services managed**: 
- apache2 (restarted after configuration change)
- sshd (restarted after configuration change)

## Template Modernization

No templates present in current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocols`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_services`: list, default: ["apache2", "sshd"], description: "Services to restart after SSL configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (configurable variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (input validation)

**Services to check**: 
- apache2 (SSL configuration applied and service running)
- sshd (service restarted successfully)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest

# Check SSL protocol configuration
sudo grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify services are running
sudo systemctl status apache2
sudo systemctl status sshd

# Test SSL configuration with openssl
echo | openssl s_client -connect localhost:443 -tls1_2 2>/dev/null | grep "Protocol"

# Verify POODLE vulnerability is mitigated
nmap --script ssl-poodle localhost -p 443
```

## Critical Issues to Address

1. **Handler Naming Inconsistency**: The task notifies "Restart apache2" but the handler is named "Restart apache" - this will cause the handler to never execute.

2. **Hardcoded Paths**: The Apache configuration path is hardcoded and should be made configurable for different distributions.

3. **Missing Error Handling**: No validation that the SSL configuration file exists before attempting to modify it.

4. **Service Dependencies**: Both Apache and SSH are restarted, but there's no clear reason why SSH needs to be restarted for an Apache SSL fix.

5. **No Backup Strategy**: The replace operation doesn't create a backup of the original configuration.

## Recommended Modern Role Structure

The modernized role should include:
- Proper variable defaults for different OS distributions
- Backup creation before configuration changes
- Validation of SSL configuration syntax
- Conditional service restarts based on actual changes
- Support for multiple SSL/TLS protocol configurations
- Integration with Ansible Vault for sensitive configurations