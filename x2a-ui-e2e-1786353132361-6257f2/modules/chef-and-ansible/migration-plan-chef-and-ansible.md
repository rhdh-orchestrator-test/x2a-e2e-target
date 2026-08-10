---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for this Ansible content.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks demonstrating how to set up a secure Apache web server with HTTPS support, along with Chef InSpec tests for validation. The migration needs focus on modernizing the playbook syntax to use FQCN, proper boolean values, and structured loops.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server with specific version
- Configures SSL/TLS for HTTPS
- Creates self-signed certificates
- Sets up a virtual host for a "Hello World" website
- Implements security hardening (POODLE vulnerability fix)
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

**Documentation:**
README.md
index.html

## Module Explanation

The repository performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache 2.4.41
   - Installs curl, openssl, and PyOpenSSL
   - Creates directory for SSL certificates
   - Generates self-signed SSL certificates
   - Configures a virtual host for a "Hello World" website
   - Disables default site and enables the new virtual host with SSL
   - Legacy patterns found: short module names, unquoted boolean values, command module without changed_when
   - Modern equivalent: FQCN module names, quoted boolean values, command with changed_when or ansible.builtin.shell with creates/removes

2. **poodle_fix.yml**:
   - Updates Apache SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Legacy patterns found: short module names, no mode for file operations
   - Modern equivalent: FQCN module names, proper file permissions

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `update_cache=true` | `update_cache: true` | website_https.yml | Key-value syntax |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN with collection |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN with collection |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN with collection |
| Missing `changed_when` | Add `changed_when` conditions | website_https.yml | For command modules |
| Missing file modes | Add `mode: '0644'` | poodle_fix.yml | For file operations |
| Unstructured handler names | Consistent handler names | website_https.yml, poodle_fix.yml | "Restart apache" vs "Restart apache2" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"
- ansible.posix: ">=1.0.0"

**External packages**:
- apache2=2.4.41-4ubuntu3.10
- curl
- openssl
- python3-openssl

**Services managed**:
- apache2
- sshd

## Template Modernization

No traditional Jinja2 templates are used in this repository. The playbooks use inline templates via vars.

## Argument Specification

Since this is not a traditional role but a set of playbooks, argument specifications would be created if converting to a role:

- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `ssl_cert_path`: string, default: "/etc/apache2/certs", description: "Path to store SSL certificates"
- `virtual_host_name`: string, default: "helloworld", description: "Name of the virtual host"
- `document_root`: string, default: "/var/www/helloworld", description: "Document root for the website"

## Checks for the Migration

**Files to verify**:
- website_https.yml (modernized)
- poodle_fix.yml (modernized)
- meta/main.yml (new)
- defaults/main.yml (new)
- tasks/main.yml (new)
- handlers/main.yml (new)
- collections/requirements.yml (new)

**Services to check**:
- apache2 (status, configuration)
- sshd (status)

**Templates to validate**:
- Virtual host configuration
- SSL configuration

## Pre-flight checks:
```
# Verify Apache is installed with correct version
dpkg -l | grep apache2

# Verify Apache is running with SSL
systemctl status apache2
apache2ctl -M | grep ssl

# Verify SSL configuration
openssl s_client -connect localhost:443 -tls1_2

# Verify website is accessible
curl -k https://localhost/

# Verify SSL protocols (no SSLv3)
nmap --script ssl-enum-ciphers -p 443 localhost
```

## Migration Strategy

To convert these playbooks into a proper Ansible role:

1. Create standard role directory structure:
   - Create tasks/main.yml with tasks from website_https.yml
   - Create handlers/main.yml with handlers from both playbooks
   - Create defaults/main.yml with variables
   - Create meta/main.yml with role metadata

2. Parameterize hardcoded values:
   - Extract inline templates to templates directory
   - Move hardcoded values to variables in defaults/main.yml

3. Add proper idempotency:
   - Replace command modules with appropriate modules
   - Add changed_when conditions where needed

4. Create collections/requirements.yml with dependencies

This migration will transform the demonstration playbooks into a reusable Ansible role following modern best practices.