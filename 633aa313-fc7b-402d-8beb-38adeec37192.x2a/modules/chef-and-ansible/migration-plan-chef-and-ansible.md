---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a set of Ansible playbooks with Chef InSpec tests for compliance validation. The module sets up an Apache web server with HTTPS enabled using self-signed certificates and includes security hardening for SSL/TLS protocols.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: TLSv1.2 only, self-signed certificates, SSL enabled

## File Structure

```
No Chef recipes found
No Chef providers found
No Chef templates found
No Chef attributes found
```

## Module Explanation

This is not a traditional Chef cookbook but rather a set of Ansible playbooks with Chef InSpec tests for compliance validation. The module already contains Ansible code, so a migration is not necessary in the traditional sense. However, I'll document the existing Ansible functionality for clarity:

1. **website_https.yml** (`chef-and-ansible/website_https.yml`):
   - Updates apt cache
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs curl, openssl, and python3-openssl
   - Creates directory for certificates at /etc/apache2/certs
   - Generates self-signed SSL certificates:
     - Private key: /etc/apache2/certs/apache.key
     - CSR: /etc/apache2/certs/apache.csr
     - Certificate: /etc/apache2/certs/apache.crt
   - Configures Apache virtual host for HTTPS:
     - Creates config at /etc/apache2/sites-available/helloworld.conf
     - Sets up DocumentRoot at /var/www/helloworld
     - Enables SSL with the generated certificates
   - Creates website directory at /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default virtual host
   - Enables the new virtual host
   - Activates SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml** (`chef-and-ansible/poodle_fix.yml`):
   - Hardens SSL configuration in Apache to mitigate POODLE vulnerability
   - Modifies /etc/apache2/mods-available/ssl.conf to disable all SSL protocols except TLSv1.2
   - Restarts Apache and SSH services after changes
   - Resources: replace, service

3. **Tests** (`chef-and-ansible/tests/website_https_verify.rb`):
   - Verifies port 443 is listening
   - Checks HTTPS response returns 200 status code
   - Confirms page content contains "Hello, world!"
   - Validates SSL3 protocol is disabled
   - Validates TLSv1.2 protocol is enabled

4. **SSH Security Test** (`chef-and-ansible/tests/ssh_profile.rb`):
   - Compliance test to ensure SSH root login is disabled
   - Checks /etc/ssh/sshd_config for PermitRootLogin setting

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

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /etc/apache2/mods-available/ssl.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.csr
- /etc/apache2/certs/apache.crt

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Apache virtual host configuration (inline in playbook) → /etc/apache2/sites-available/helloworld.conf
- HTML content (inline in playbook) → /var/www/helloworld/index.html

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module

# SSL/TLS configuration
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol
# Should show: SSLProtocol -all +TLSv1.2

# Certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout
ls -la /etc/apache2/certs/

# Website content
cat /var/www/helloworld/index.html
grep -r "Hello, world" /var/www/helloworld/

# Virtual host configuration
cat /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/ | grep helloworld

# HTTPS connectivity
curl -k https://localhost/
curl -k -I https://localhost/  # Should return HTTP 200

# SSL/TLS protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost
# Should show TLSv1.2 enabled, SSLv3 disabled

# Port listening
netstat -tulpn | grep :443
ss -tlnp | grep :443

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# SSH security (if applicable)
grep PermitRootLogin /etc/ssh/sshd_config
# Should NOT show "PermitRootLogin yes"
```