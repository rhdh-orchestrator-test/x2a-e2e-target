---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not actually a Chef cookbook but a demonstration of using Chef InSpec for compliance testing with Ansible playbooks. The repository contains Ansible playbooks for configuring a secure HTTPS website and fixing SSL vulnerabilities, along with InSpec tests to verify compliance.

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

The repository contains Ansible playbooks with InSpec tests for compliance verification:

1. **website_https.yml**:
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates certificate directory: /etc/apache2/certs
   - Generates self-signed SSL certificate using OpenSSL
   - Configures Apache virtual host for HTTPS on port 443
   - Creates website directory: /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default site and enables the new HTTPS site
   - Enables SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml**:
   - Addresses the POODLE vulnerability by disabling SSLv3
   - Updates Apache SSL configuration to only allow TLSv1.2
   - Modifies /etc/apache2/mods-available/ssl.conf
   - Resources: replace, service

3. **InSpec Tests**:
   - **tests/website_https_verify.rb**:
     - Verifies port 443 is listening
     - Checks HTTPS response returns status 200
     - Confirms page content contains "Hello, world!"
     - Validates SSL3 is disabled
     - Validates TLS 1.2 is enabled
   
   - **tests/ssh_profile.rb**:
     - Security compliance test for SSH configuration
     - Verifies root login is disabled in SSH
     - Includes security tags and compliance information
     - Provides remediation guidance

## Dependencies

**External cookbook dependencies**: None (this is not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this repository. All configuration values appear to be non-sensitive. The SSL certificates are generated during playbook execution and are not pre-existing secrets.

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
- Apache virtual host configuration (inline template in website_https.yml)
- HTML content (inline template in website_https.yml)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
systemctl status sshd

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module enabled

# SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2  # Should connect successfully
openssl s_client -connect localhost:443 -ssl3    # Should fail to connect

# Website accessibility
curl -k https://localhost/  # Should return HTTP 200 with "Hello, world!" content
curl -k -I https://localhost/  # Should show HTTP/1.1 200 OK

# Certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout  # Check certificate details
ls -la /etc/apache2/certs/  # Verify permissions on certificate files

# Virtual host configuration
grep -r "SSLEngine on" /etc/apache2/sites-enabled/
grep -r "DocumentRoot" /etc/apache2/sites-enabled/ | grep helloworld

# SSL protocol configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf  # Should show "-all +TLSv1.2"

# SSH security configuration
grep "PermitRootLogin" /etc/ssh/sshd_config  # Should not be set to "yes"

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep :443
lsof -i :443

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
journalctl -u apache2 -f
```