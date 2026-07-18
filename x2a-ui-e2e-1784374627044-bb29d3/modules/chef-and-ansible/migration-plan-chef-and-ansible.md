---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The playbooks configure an Apache web server with HTTPS support and SSL security hardening. The migration needs to focus on modernizing the playbook syntax to use FQCN, proper boolean values, and modern loop structures.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs Apache web server
- Configures HTTPS with self-signed certificates
- Deploys a simple "Hello World" website
- Hardens SSL/TLS configuration (disables SSLv3, enables TLSv1.2)
- Uses Chef InSpec for compliance testing

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

```
README.md
index.html
kitchen.yml
poodle_fix.yml
tests/ssh_profile.rb
tests/website_https_verify.rb
website_https.yml
```

**Playbook Files:**
website_https.yml
poodle_fix.yml

**Test Files:**
tests/website_https_verify.rb
tests/ssh_profile.rb

**Configuration Files:**
kitchen.yml

**Static Files:**
index.html
README.md

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache web server and dependencies
   - Creates SSL certificates directory
   - Generates self-signed SSL certificates
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys content
   - Activates the virtual host and SSL module
   - Restarts services when needed

2. **poodle_fix.yml**:
   - Hardens SSL configuration by disabling vulnerable protocols
   - Enables only TLSv1.2
   - Restarts Apache and SSH services

3. **Tests**:
   - Uses Chef InSpec to verify HTTPS is working
   - Verifies SSL/TLS security configuration
   - Checks SSH security configuration

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `apt: update_cache=true` | `ansible.builtin.apt: update_cache=true` | website_https.yml | FQCN |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `update_cache=true` | `update_cache: true` | website_https.yml | Boolean syntax |
| `force: yes` | `force: true` | website_https.yml | Boolean syntax |
| Missing `changed_when` | Add `changed_when` conditions | website_https.yml | For command modules |
| Missing handler name | Fix handler name mismatch | poodle_fix.yml | "Restart apache2" vs "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**External packages**:
- apache2
- curl
- openssl
- python3-openssl

**Services managed**:
- apache2
- sshd

## Template Modernization

No traditional Jinja2 templates are used in this module. However, the inline templates in the playbooks should be reviewed:

- **website_https.yml**: The `conftext` and `webtext` variables contain inline templates that should be moved to separate template files using `ansible.builtin.template` for better maintainability.

## Argument Specification

For a proper role conversion, these variables should be documented in meta/argument_specs.yml:

- `conftext`: string, Apache virtual host configuration
- `webtext`: string, HTML content for the website

## Checks for the Migration

**Files to verify**:
- tasks/main.yml (new file to be created)
- handlers/main.yml (new file to be created)
- templates/virtualhost.conf.j2 (new file to be created)
- templates/index.html.j2 (new file to be created)
- defaults/main.yml (new file to be created)
- meta/main.yml (new file to be created)
- meta/argument_specs.yml (new file to be created)

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/virtualhost.conf.j2
- templates/index.html.j2

## Pre-flight checks:
```
# Verify Apache configuration
apache2ctl configtest

# Verify SSL configuration
openssl s_client -connect localhost:443 -tls1_2

# Verify website is accessible
curl -k https://localhost/

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```

## Migration Notes

This is not a traditional Ansible role but rather a set of playbooks with Chef InSpec tests. To properly migrate this to a modern Ansible role:

1. Create a standard Ansible role structure:
   - tasks/main.yml
   - handlers/main.yml
   - templates/
   - defaults/main.yml
   - meta/main.yml

2. Move the inline templates to proper template files:
   - Move `conftext` to templates/virtualhost.conf.j2
   - Move `webtext` to templates/index.html.j2

3. Convert the Chef InSpec tests to Ansible Molecule tests for proper integration testing within the Ansible ecosystem.

4. Create a proper role metadata file with dependencies and supported platforms.

5. Document all variables in defaults/main.yml with proper comments.