---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing alongside Ansible. The module contains Ansible playbooks for configuring a secure Apache web server with HTTPS and InSpec tests for verifying compliance.

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
README.md
index.html
kitchen.yml
```

## Module Explanation

The module demonstrates using Chef InSpec for compliance testing with Ansible deployments:

1. **website_https.yml**:
   - Installs Apache 2.4.41 web server package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates certificate directory: /etc/apache2/certs
   - Generates self-signed SSL certificate and key
   - Configures Apache virtual host for HTTPS
   - Creates web content directory: /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Resources: apt (3), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml**:
   - Updates Apache SSL configuration to mitigate POODLE vulnerability
   - Disables SSLv3 and enables only TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace (1), service (2)

3. **tests/website_https_verify.rb** (InSpec test):
   - Verifies port 443 is listening
   - Checks HTTPS response returns status 200
   - Confirms "Hello, world!" text appears in response
   - Validates SSL3 is disabled
   - Validates TLS 1.2 is enabled
   - Resources: port (1), http (1), ssl (2)

4. **tests/ssh_profile.rb** (InSpec test):
   - Validates SSH root login is disabled
   - Checks for proper SSH configuration
   - Includes security rationale and compliance metadata
   - Resources: sshd_config (1), package (1)

## Dependencies

**External cookbook dependencies**: None (this is not a traditional Chef cookbook)

**System package dependencies**: 
- apache2 (version 2.4.41-4ubuntu3.10)
- curl
- openssl
- python3-openssl

**Service dependencies**: 
- apache2
- sshd

## Credentials

**Detection Summary**: No credentials detected across files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive. The SSL certificates are generated during deployment rather than stored in the repository.

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
ls -la /etc/apache2/sites-enabled/  # Verify helloworld.conf is enabled
ls -la /etc/apache2/sites-available/  # Verify helloworld.conf exists
cat /etc/apache2/sites-available/helloworld.conf  # Check virtual host config
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf  # Should show "SSLProtocol -all +TLSv1.2"

# Certificate verification
ls -la /etc/apache2/certs/  # Check certificate files exist
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout  # Verify certificate details

# Web content verification
ls -la /var/www/helloworld/  # Check web content directory
cat /var/www/helloworld/index.html  # Verify HTML content

# HTTPS connectivity
curl -k https://localhost/  # Should return HTML with "Hello, world!"
curl -I -k https://localhost/  # Should return HTTP 200

# SSL/TLS protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost  # Should show TLS 1.2 enabled, SSL3 disabled

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log

# SSH configuration (for compliance)
grep "PermitRootLogin" /etc/ssh/sshd_config  # Should not be set to "yes"
```