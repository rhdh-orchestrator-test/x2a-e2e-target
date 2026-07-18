---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather an example of using Chef InSpec with Ansible. The module contains Ansible playbooks that set up an Apache web server with HTTPS support and SSL security fixes, along with InSpec tests for verification.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS**: A single Apache web server instance
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

This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec with Ansible. The module contains Ansible playbooks that are already in Ansible format, along with InSpec tests for verification.

The Ansible playbooks perform operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs curl, openssl, and python3-openssl
   - Creates a directory for SSL certificates at /etc/apache2/certs
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures a virtual host for HTTPS
   - Creates a "Hello World" website in /var/www/helloworld
   - Disables the default virtual host and enables the new one
   - Enables SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Sets SSLProtocol to "-all +TLSv1.2" to only allow TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace, service

The InSpec tests verify:
- Port 443 is listening
- HTTPS website returns status 200 and contains "Hello, world!"
- SSL3 protocol is disabled
- TLS1.2 protocol is enabled
- SSH root login is disabled (separate security check)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.csr
- /etc/apache2/certs/apache.crt
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Virtual host configuration (rendered once)
- Website HTML content (rendered once)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Web server configuration
apachectl -t
apachectl -M | grep ssl
cat /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/
ls -la /var/www/helloworld/

# SSL certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout
openssl verify -CAfile /etc/apache2/certs/apache.crt /etc/apache2/certs/apache.crt

# SSL protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost
openssl s_client -connect localhost:443 -tls1_2
# Should succeed
openssl s_client -connect localhost:443 -ssl3
# Should fail

# Website accessibility
curl -k https://localhost/
curl -k -I https://localhost/
# Should return 200 OK and contain "Hello, world!"

# SSL configuration check
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf
# Should show: SSLProtocol -all +TLSv1.2

# SSH security check (additional test)
grep "PermitRootLogin" /etc/ssh/sshd_config
# Should NOT show "PermitRootLogin yes"

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache
lsof -i :443

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log
```