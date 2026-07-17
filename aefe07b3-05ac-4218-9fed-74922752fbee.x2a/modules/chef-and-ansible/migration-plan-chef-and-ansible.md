---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather an example of using Chef InSpec with Ansible. The module contains Ansible playbooks that set up an Apache web server with HTTPS support and SSL security fixes, along with InSpec tests for validation.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: TLSv1.2 enabled, SSLv3 disabled, self-signed certificate

## File Structure

```
website_https.yml
poodle_fix.yml
tests/website_https_verify.rb
tests/ssh_profile.rb
kitchen.yml
README.md
index.html
```

## Module Explanation

The module contains Ansible playbooks that perform operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs curl, openssl, and python3-openssl
   - Creates directory for certificates at /etc/apache2/certs
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web root directory at /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default virtual host and enables the new one
   - Enables SSL module in Apache
   - Resources: apt (2), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Sets SSLProtocol to allow only TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace (1), service (2)

3. **Test Verification**:
   - **tests/website_https_verify.rb**: InSpec tests to verify:
     - Port 443 is listening
     - HTTPS site returns 200 status and contains "Hello, world!"
     - SSLv3 is disabled
     - TLSv1.2 is enabled
   - **tests/ssh_profile.rb**: InSpec test to verify SSH root login is disabled

## Dependencies

**External cookbook dependencies**: None (this is an Ansible playbook with InSpec tests)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive. The SSL certificates are generated during playbook execution and are not pre-existing secrets.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.crt
- /etc/apache2/certs/apache.csr
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Apache virtual host configuration (inline template in website_https.yml)
- HTML content (inline template in website_https.yml)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
systemctl status sshd

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl

# SSL configuration
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol
openssl s_client -connect localhost:443 -tls1_2
openssl s_client -connect localhost:443 -ssl3 # Should fail

# Virtual host configuration
ls -la /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/helloworld.conf
cat /etc/apache2/sites-available/helloworld.conf

# Certificate verification
ls -la /etc/apache2/certs/
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Website content
ls -la /var/www/helloworld/
cat /var/www/helloworld/index.html

# Website accessibility
curl -k https://localhost/ | grep "Hello, world!"
curl -I -k https://localhost/

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# SSH security check
grep PermitRootLogin /etc/ssh/sshd_config
```