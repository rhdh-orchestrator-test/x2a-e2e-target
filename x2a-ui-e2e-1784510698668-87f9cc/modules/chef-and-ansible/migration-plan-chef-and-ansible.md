---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing alongside Ansible. The module contains Ansible playbooks for deploying a secure HTTPS website with Apache and InSpec tests to verify compliance.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS website**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled with self-signed certificate, TLSv1.2 protocol

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
   - Creates SSL certificate directory at /etc/apache2/certs
   - Generates self-signed SSL certificate using OpenSSL
   - Configures Apache virtual host for HTTPS
   - Creates website content directory at /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Enables SSL module in Apache
   - Disables default site and enables the new virtual host
   - Resources: apt (3), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml**:
   - Addresses SSL POODLE vulnerability by modifying Apache SSL configuration
   - Updates /etc/apache2/mods-available/ssl.conf to disable all protocols except TLSv1.2
   - Restarts Apache and SSH services after changes
   - Resources: replace (1), service (2)

3. **InSpec Tests**:
   - **tests/website_https_verify.rb**: Verifies HTTPS website functionality and security
     - Checks port 443 is listening
     - Verifies HTTPS response contains "Hello, world!"
     - Ensures SSLv3 is disabled (POODLE vulnerability mitigation)
     - Confirms TLSv1.2 is enabled
   - **tests/ssh_profile.rb**: Verifies SSH security compliance
     - Checks that SSH root login is disabled
     - Includes detailed compliance metadata (STIG IDs, CCI references)

## Dependencies

**External cookbook dependencies**: None (not a traditional Chef cookbook)
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
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.crt
- /etc/apache2/certs/apache.csr
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Apache virtual host configuration (inline template → /etc/apache2/sites-available/helloworld.conf)
- HTML content (inline template → /var/www/helloworld/index.html)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Web server configuration
apache2ctl -t
apache2ctl -M | grep ssl
ls -la /etc/apache2/sites-enabled/
cat /etc/apache2/sites-available/helloworld.conf

# SSL certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout
ls -la /etc/apache2/certs/

# SSL protocol verification
openssl s_client -connect localhost:443 -tls1_2
# Should connect successfully

openssl s_client -connect localhost:443 -ssl3
# Should fail with "wrong version number" or similar

# Website content and accessibility
curl -k https://localhost/
# Should return HTML with "Hello, world!"

# Check for POODLE fix
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf
# Should show: SSLProtocol -all +TLSv1.2

# SSH security check
grep "PermitRootLogin" /etc/ssh/sshd_config
# Should NOT show "PermitRootLogin yes"

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep :443
lsof -i :443

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
```