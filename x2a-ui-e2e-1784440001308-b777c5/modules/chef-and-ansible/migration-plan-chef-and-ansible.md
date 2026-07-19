---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec with Ansible. The repository contains Ansible playbooks that set up an Apache web server with HTTPS and security hardening, along with InSpec tests to verify compliance.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Server**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: TLS 1.2 enabled, SSL3 disabled, self-signed certificate

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

The repository performs operations in this order:

1. **website_https.yml**:
   - Installs Apache 2.4.41-4ubuntu3.10 package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates: /etc/apache2/certs
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web root directory: /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default virtual host and enables the new one
   - Enables SSL module in Apache
   - Resources: apt (2), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Modifies /etc/apache2/mods-available/ssl.conf to use only TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace (1), service (2)

3. **Testing with InSpec**:
   - **tests/website_https_verify.rb**: Verifies that:
     - Port 443 is listening
     - HTTPS site returns 200 status and contains "Hello, world!"
     - SSL3 protocol is disabled
     - TLS 1.2 protocol is enabled
   - **tests/ssh_profile.rb**: Verifies SSH security compliance:
     - Ensures root login is disabled via SSH
     - Checks for proper SSH configuration

## Dependencies

**External cookbook dependencies**: None (This is not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this repository. All configuration values appear to be non-sensitive. The SSL certificates are generated during deployment rather than being stored in the repository.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /etc/apache2/sites-enabled/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.crt
- /etc/apache2/certs/apache.csr
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Apache virtual host configuration (rendered once)
- HTML content (rendered once)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
systemctl status sshd

# Apache configuration validation
apache2ctl configtest
apachectl -M | grep ssl  # Verify SSL module is enabled

# SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2 </dev/null
openssl s_client -connect localhost:443 -ssl3 </dev/null  # Should fail

# Virtual host configuration
grep -r "DocumentRoot" /etc/apache2/sites-enabled/
ls -la /etc/apache2/sites-enabled/  # Should show helloworld.conf
ls -la /etc/apache2/sites-available/  # Should show helloworld.conf
cat /etc/apache2/sites-available/helloworld.conf

# Certificate verification
ls -la /etc/apache2/certs/
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Website content
ls -la /var/www/helloworld/
cat /var/www/helloworld/index.html | grep "Hello, world!"

# HTTPS functionality
curl -k https://localhost/ | grep "Hello, world!"
curl -I -k https://localhost/  # Should return HTTP 200

# SSL protocol settings
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf  # Should show "-all +TLSv1.2"

# SSH security settings
grep "PermitRootLogin" /etc/ssh/sshd_config  # Should not be "yes"

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache
```