---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a set of Ansible playbooks with Chef InSpec tests for compliance validation. The module deploys an Apache web server with HTTPS enabled using a self-signed certificate and implements security hardening for SSL/TLS protocols.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS site**: A single Apache web server instance
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
index.html
```

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache 2.4.41-4ubuntu3.10 package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates at /etc/apache2/certs
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web root directory at /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default Apache site and enables the new virtual host
   - Enables SSL module in Apache
   - Resources: apt (2), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml**:
   - Updates Apache SSL configuration to disable vulnerable protocols
   - Sets SSLProtocol to "-all +TLSv1.2" to only allow TLS 1.2
   - Restarts Apache and SSH services
   - Resources: replace (1), service (2)

3. **Tests**:
   - **tests/website_https_verify.rb**: Verifies that port 443 is listening, the website returns a 200 status code with "Hello, world!" content, SSL3 is disabled, and TLS 1.2 is enabled
   - **tests/ssh_profile.rb**: Ensures SSH root login is disabled for security compliance

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

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive. The SSL certificates are generated during deployment rather than being stored in the repository.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /etc/apache2/sites-enabled/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.csr
- /etc/apache2/certs/apache.crt
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Apache virtual host configuration (rendered once)
- HTML content (rendered once)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module

# Virtual host configuration
cat /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/ | grep helloworld

# SSL configuration
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout  # Check certificate details

# Website accessibility
curl -k https://localhost/
curl -k -I https://localhost/  # Should return HTTP 200

# SSL/TLS protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost  # Should show TLS 1.2 enabled, SSL3 disabled

# Directory and file permissions
ls -la /var/www/helloworld/
ls -la /etc/apache2/certs/

# Content verification
grep "Hello, world!" /var/www/helloworld/index.html

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# SSH security (related to the compliance test)
grep PermitRootLogin /etc/ssh/sshd_config
```