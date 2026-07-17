---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a Chef cookbook but an Ansible playbook with Chef InSpec tests. The repository demonstrates how to use Chef InSpec for compliance testing alongside Ansible deployments. The playbook sets up an Apache web server with HTTPS enabled using a self-signed certificate.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache2**: Web server with HTTPS enabled
  - Location/Path: /etc/apache2
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled with TLSv1.2, self-signed certificate

## File Structure

```
No Chef recipes found. This is an Ansible playbook repository.

No Chef providers found.

No Chef templates found.

No Chef attributes found.
```

## Module Explanation

This is not a Chef cookbook but an Ansible playbook with Chef InSpec tests. The repository demonstrates how to use Chef InSpec for compliance testing alongside Ansible deployments.

The Ansible playbook performs the following operations:

1. **website_https.yml**:
   - Installs Apache 2.4.41-4ubuntu3.10 package
   - Installs curl, openssl, and python3-openssl packages
   - Creates a directory for SSL certificates at /etc/apache2/certs
   - Generates a self-signed SSL certificate for HTTPS
   - Configures a virtual host for a "Hello World" website on HTTPS (port 443)
   - Deploys a simple HTML page with "Hello, world!" content
   - Disables the default Apache site and enables the new virtual host
   - Enables SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Sets SSLProtocol to allow only TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace, service

3. **tests/website_https_verify.rb**:
   - Chef InSpec test to verify:
     - Port 443 is listening
     - HTTPS website returns 200 status code
     - Website content contains "Hello, world!"
     - SSL3 protocol is disabled
     - TLS 1.2 protocol is enabled

4. **tests/ssh_profile.rb**:
   - Chef InSpec test to verify SSH root login is disabled
   - Checks sshd_config for PermitRootLogin setting

## Dependencies

**External cookbook dependencies**: None (not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

No credentials or secrets were detected in this repository. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.crt
- /etc/apache2/certs/apache.csr
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (*)

**Templates rendered**:
- No Chef templates, but Ansible variables are used to create:
  - helloworld.conf (Apache virtual host configuration)
  - index.html (Website content)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl

# SSL certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout
openssl verify -CAfile /etc/apache2/certs/apache.crt /etc/apache2/certs/apache.crt

# SSL protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost
openssl s_client -connect localhost:443 -tls1_2
openssl s_client -connect localhost:443 -ssl3 # Should fail

# Website accessibility
curl -k https://localhost/
curl -k -I https://localhost/

# Configuration validation
cat /etc/apache2/sites-available/helloworld.conf
cat /var/www/helloworld/index.html
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache2
lsof -i :443

# Enabled sites and modules
ls -la /etc/apache2/sites-enabled/
ls -la /etc/apache2/mods-enabled/ | grep ssl
```