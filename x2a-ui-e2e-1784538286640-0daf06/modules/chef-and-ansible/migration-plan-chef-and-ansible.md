---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a collection of standalone playbooks that configure an Apache web server with HTTPS support and SSL security hardening. The migration needs to focus on converting these standalone playbooks into a proper Ansible role structure with modern syntax, including FQCN module names, proper boolean values, and structured organization.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server
- Configures HTTPS with self-signed certificates
- Deploys a simple "Hello World" website
- Implements SSL security hardening (POODLE vulnerability fix)
- Sets up SSL/TLS protocols for security compliance

## File Structure

**IMPORTANT: The source is not structured as an Ansible role but as standalone playbooks. Below is the current structure:**

```
README.md
index.html
kitchen.yml
poodle_fix.yml
tests/ssh_profile.rb
tests/website_https_verify.rb
website_https.yml
```

**Proposed Role Structure:**

```
tasks/main.yml
tasks/apache.yml
tasks/ssl.yml
tasks/security.yml
handlers/main.yml
templates/virtualhost.conf.j2
templates/index.html.j2
defaults/main.yml
meta/main.yml
tests/inspec/website_https_verify.rb
tests/inspec/ssh_profile.rb
```

## Module Explanation

The current implementation performs operations in this order:

1. **website_https.yml** (standalone playbook):
   - Updates apt cache
   - Installs Apache and SSL-related packages
   - Creates directories for SSL certificates
   - Generates self-signed SSL certificates
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys HTML content
   - Disables default site and enables custom site
   - Enables SSL module in Apache
   - Includes handlers for restarting Apache and SSH services

2. **poodle_fix.yml** (standalone playbook):
   - Modifies Apache SSL configuration to mitigate POODLE vulnerability
   - Includes handlers for restarting Apache and SSH services

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt: update_cache=true` | `ansible.builtin.apt: update_cache: true` | website_https.yml | FQCN and boolean syntax |
| `apt: name: apache2=2.4.41-4ubuntu3.10` | `ansible.builtin.apt: name: apache2=2.4.41-4ubuntu3.10` | website_https.yml | FQCN |
| `apt: pkg:` | `ansible.builtin.apt: pkg:` | website_https.yml | FQCN |
| `file: path: /etc/apache2/certs state: directory mode: 0640` | `ansible.builtin.file: path: /etc/apache2/certs state: directory mode: '0640'` | website_https.yml | FQCN and quoted mode |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN |
| `copy: content: "{{ conftext }}"` | `ansible.builtin.copy: content: "{{ conftext }}"` | website_https.yml | FQCN |
| `command: a2dissite 000-default` | `ansible.builtin.command: a2dissite 000-default` with `changed_when:` | website_https.yml | FQCN and idempotency |
| `command: a2ensite helloworld` | `ansible.builtin.command: a2ensite helloworld` with `changed_when:` | website_https.yml | FQCN and idempotency |
| `command: a2enmod ssl` | `ansible.builtin.command: a2enmod ssl` with `changed_when:` | website_https.yml | FQCN and idempotency |
| `replace: dest=/etc/apache2/mods-available/ssl.conf` | `ansible.builtin.replace: path: /etc/apache2/mods-available/ssl.conf` | poodle_fix.yml | FQCN and parameter name change (dest → path) |
| Inline templates | Move to template files | website_https.yml | Move `conftext` and `webtext` to template files |
| Standalone playbooks | Role structure | All files | Convert to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.9.0"
- ansible.posix: ">=1.3.0"

**Role dependencies**: None specified in current implementation

**External packages**:
- apache2
- curl
- openssl
- python3-openssl

**Services managed**:
- apache2
- sshd

## Template Modernization

- **virtualhost.conf.j2**: Create from inline `conftext` variable in website_https.yml
- **index.html.j2**: Create from inline `webtext` variable in website_https.yml

## Argument Specification

Variables that should be in meta/argument_specs.yml:

- **apache_version**: 
  - type: str
  - default: "2.4.41-4ubuntu3.10"
  - description: Version of Apache to install
  
- **website_root**: 
  - type: str
  - default: "/var/www/helloworld"
  - description: Directory path for website files
  
- **ssl_cert_dir**: 
  - type: str
  - default: "/etc/apache2/certs"
  - description: Directory for SSL certificates
  
- **ssl_protocols**: 
  - type: str
  - default: "-all +TLSv1.2"
  - description: SSL protocols to enable/disable

- **website_domain**:
  - type: str
  - default: "myhost"
  - description: Domain name for the website

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- tasks/apache.yml
- tasks/ssl.yml
- tasks/security.yml
- handlers/main.yml
- templates/virtualhost.conf.j2
- templates/index.html.j2
- defaults/main.yml
- meta/main.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/virtualhost.conf.j2
- templates/index.html.j2

## Pre-flight checks:

```bash
# Check Apache configuration
apache2ctl configtest

# Check SSL configuration
openssl s_client -connect localhost:443 -tls1_2

# Verify website is accessible
curl -k https://localhost/

# Verify SSL protocols
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify Apache is running with SSL
systemctl status apache2
```