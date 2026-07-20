---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing alongside Ansible. The repository contains Ansible playbooks for configuring a secure Apache web server with HTTPS and InSpec tests for verifying compliance.

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

This repository demonstrates using Chef InSpec for compliance testing alongside Ansible deployments. The Ansible playbooks perform the following operations:

1. **website_https.yml**:
   - Installs Apache 2.4.41-4ubuntu3.10 package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates certificate directory: /etc/apache2/certs
   - Generates self-signed SSL certificate:
     - Private key: /etc/apache2/certs/apache.key
     - CSR: /etc/apache2/certs/apache.csr
     - Certificate: /etc/apache2/certs/apache.crt
   - Configures Apache virtual host for HTTPS:
     - Template: Inline template → /etc/apache2/sites-available/helloworld.conf
   - Creates web content directory: /var/www/helloworld
   - Deploys website content:
     - Template: Inline template → /var/www/helloworld/index.html
   - Disables default site: a2dissite 000-default
   - Enables new site: a2ensite helloworld
   - Enables SSL module: a2enmod ssl
   - Resources: apt (3), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml**:
   - Updates SSL configuration to mitigate POODLE vulnerability:
     - Modifies /etc/apache2/mods-available/ssl.conf to disable SSL3 and enable only TLSv1.2
   - Resources: replace (1), service (2)

3. **InSpec Tests**:
   - **tests/website_https_verify.rb**:
     - Verifies port 443 is listening
     - Checks HTTPS response returns 200 status and contains "Hello, world!"
     - Confirms SSL3 is disabled
     - Confirms TLS 1.2 is enabled
   
   - **tests/ssh_profile.rb**:
     - Verifies SSH root login is disabled for security compliance
     - Includes STIG references and compliance metadata

## Dependencies

**External cookbook dependencies**: None (this is not a traditional Chef cookbook)

**System package dependencies**: 
- apache2 (version 2.4.41-4ubuntu3.10)
- curl
- openssl
- python3-openssl
- openssh-server (implied by tests)

**Service dependencies**: 
- apache2
- sshd

## Credentials

**Detection Summary**: No credentials detected across files

No credentials or secrets were detected in this repository. All configuration values appear to be non-sensitive. The SSL certificates are generated during deployment rather than being stored in the repository.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.csr
- /etc/apache2/certs/apache.crt
- /etc/apache2/mods-available/ssl.conf
- /etc/ssh/sshd_config

**Service endpoints to check**:
- Ports listening: 443
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Apache virtual host config (rendered once)
- Website HTML content (rendered once)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
systemctl status sshd

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module

# SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2  # Should connect successfully
openssl s_client -connect localhost:443 -ssl3    # Should fail to connect

# Virtual host configuration
grep -r "DocumentRoot" /etc/apache2/sites-available/
grep -r "SSLEngine" /etc/apache2/sites-available/
grep -r "SSLProtocol" /etc/apache2/mods-available/ssl.conf  # Should show "SSLProtocol -all +TLSv1.2"

# Certificate verification
ls -la /etc/apache2/certs/
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"

# Website content
curl -k https://localhost/ | grep "Hello, world!"  # Should return the website content

# SSH configuration
grep "PermitRootLogin" /etc/ssh/sshd_config  # Should not be set to "yes"

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep :443
lsof -i :443

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log
journalctl -u apache2 -f
```