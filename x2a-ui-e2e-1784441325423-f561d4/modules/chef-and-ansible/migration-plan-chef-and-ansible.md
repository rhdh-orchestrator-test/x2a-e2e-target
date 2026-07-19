---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec with Ansible. The module contains Ansible playbooks that set up an Apache web server with HTTPS support and SSL security fixes, along with InSpec tests for validation.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Server**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled with self-signed certificate, TLSv1.2 protocol

## File Structure

```
No Chef recipes found
No Chef providers found
No Chef templates found
No Chef attributes found
```

## Module Explanation

This is not a traditional Chef cookbook but rather a set of Ansible playbooks with Chef InSpec tests. The module demonstrates how to use Chef InSpec for compliance testing alongside Ansible deployments.

The Ansible playbooks perform operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates at /etc/apache2/certs
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web root directory at /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Sets SSLProtocol to "-all +TLSv1.2" to only allow TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace, service

The Chef InSpec tests verify:
- Port 443 is listening
- HTTPS website returns 200 status and contains "Hello, world!"
- SSL3 protocol is disabled (security check)
- TLS 1.2 protocol is enabled
- SSH root login is disabled (security check)

## Dependencies

**External cookbook dependencies**: None (not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive. The SSL certificates are generated during deployment and are not pre-existing secrets.

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
- Apache virtual host configuration (rendered inline from variable)
- HTML content (rendered inline from variable)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
systemctl status sshd

# Apache configuration validation
apache2ctl -t
apache2ctl -M | grep ssl
cat /etc/apache2/sites-available/helloworld.conf
cat /etc/apache2/sites-enabled/helloworld.conf
ls -la /etc/apache2/sites-enabled/

# SSL configuration and certificates
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout
ls -la /etc/apache2/certs/

# Website accessibility
curl -k https://localhost/
curl -I -k https://localhost/

# SSL/TLS protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost
openssl s_client -connect localhost:443 -tls1_2
openssl s_client -connect localhost:443 -ssl3 # Should fail

# Security checks
grep PermitRootLogin /etc/ssh/sshd_config

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log
journalctl -u apache2 -f
```