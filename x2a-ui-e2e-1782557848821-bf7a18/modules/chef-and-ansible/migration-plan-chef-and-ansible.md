---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a Chef cookbook that requires migration to Ansible. The repository already contains Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) that configure an Apache web server with HTTPS. The Chef components are limited to InSpec tests for compliance verification.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Server**: A single Apache web server instance configured with SSL/TLS
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: Uses TLSv1.2, disables older protocols, serves a simple "Hello, world!" page

## File Structure

```
website_https.yml
poodle_fix.yml
tests/website_https_verify.rb
tests/ssh_profile.rb
kitchen.yml
index.html
README.md
```

## Module Explanation

The repository contains Ansible playbooks that perform the following operations:

1. **website_https.yml**:
   - Installs Apache 2.4.41 web server package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates SSL certificate directory at /etc/apache2/certs
   - Generates self-signed SSL certificate and key
   - Configures a virtual host for HTTPS on port 443
   - Creates web content directory at /var/www/helloworld
   - Deploys a simple HTML page with "Hello, world!" content
   - Disables the default virtual host and enables the new one
   - Enables SSL module in Apache
   - Resources: apt (3), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Sets SSLProtocol to use only TLSv1.2, disabling older protocols
   - Restarts Apache and SSH services after changes
   - Resources: replace (1), service (2)

The Chef InSpec tests verify:
1. **tests/website_https_verify.rb**:
   - Port 443 is listening
   - HTTPS site returns 200 status code
   - Page content contains "Hello, world!"
   - SSL3 protocol is disabled
   - TLS 1.2 protocol is enabled

2. **tests/ssh_profile.rb**:
   - SSH root login is disabled for security compliance
   - Verifies either sshd_config has PermitRootLogin not set to 'yes' or openssh-server is not installed

## Dependencies

**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

No credentials or secrets were detected in this repository. All configuration values appear to be non-sensitive. The SSL certificates are generated during playbook execution and are not pre-existing secrets.

## Checks for the Migration

Since this is already implemented in Ansible, no migration is necessary. However, for completeness, here are the verification steps:

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /etc/apache2/sites-enabled/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.crt
- /etc/apache2/certs/apache.csr
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Apache virtual host configuration (inline in playbook)
- HTML content (inline in playbook)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache

# Web server connectivity
curl -k https://localhost/
curl -k -I https://localhost/

# SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2
# Should succeed
openssl s_client -connect localhost:443 -ssl3
# Should fail - protocol not supported

# Configuration validation
apache2ctl -t
grep -r "SSLProtocol" /etc/apache2/
cat /etc/apache2/sites-enabled/helloworld.conf
ls -la /etc/apache2/certs/

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache
lsof -i :443

# File permissions
ls -la /etc/apache2/certs/
ls -la /var/www/helloworld/

# SSH security check (for poodle_fix.yml)
grep PermitRootLogin /etc/ssh/sshd_config
```