---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a set of Ansible playbooks with Chef InSpec tests for compliance validation. The module configures an Apache web server with HTTPS support using self-signed certificates and implements security hardening for SSL/TLS protocols.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: TLS 1.2 only, self-signed certificates

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
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for certificates: /etc/apache2/certs
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web root directory: /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default virtual host
   - Enables the new virtual host
   - Activates SSL module in Apache
   - Resources: apt (2), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml**:
   - Updates SSL configuration to mitigate POODLE vulnerability
   - Modifies /etc/apache2/mods-available/ssl.conf to disable all SSL protocols except TLS 1.2
   - Restarts Apache and SSH services
   - Resources: replace (1), service (2)

3. **Testing with InSpec**:
   - **tests/website_https_verify.rb**:
     - Verifies port 443 is listening
     - Checks HTTPS response returns 200 status code
     - Confirms page content contains "Hello, world!"
     - Validates SSL3 is disabled
     - Validates TLS 1.2 is enabled
   
   - **tests/ssh_profile.rb**:
     - Verifies SSH root login is disabled for security compliance
     - Checks either sshd_config has PermitRootLogin not set to 'yes' or openssh-server is not installed

## Dependencies

**External cookbook dependencies**: None (this is an Ansible playbook set)
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
apachectl -M | grep ssl  # Should show ssl_module

# SSL/TLS configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf  # Should show "SSLProtocol -all +TLSv1.2"

# Certificate verification
ls -la /etc/apache2/certs/
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"

# Virtual host configuration
ls -la /etc/apache2/sites-enabled/  # Should show helloworld.conf
cat /etc/apache2/sites-available/helloworld.conf | grep -E "VirtualHost|DocumentRoot|SSLEngine"

# Website content
ls -la /var/www/helloworld/
cat /var/www/helloworld/index.html | grep "Hello, world!"

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache2

# HTTPS connectivity
curl -k https://localhost/ | grep "Hello, world!"

# SSL/TLS protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost
openssl s_client -connect localhost:443 -tls1_2  # Should succeed
openssl s_client -connect localhost:443 -ssl3  # Should fail

# SSH security check
grep "PermitRootLogin" /etc/ssh/sshd_config  # Should not be "yes"

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
```