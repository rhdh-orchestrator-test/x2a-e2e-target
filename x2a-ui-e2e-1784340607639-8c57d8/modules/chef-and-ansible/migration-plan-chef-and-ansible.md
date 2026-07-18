---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing with Ansible playbooks. The repository contains Ansible playbooks for configuring an Apache web server with HTTPS and SSL security fixes, along with InSpec tests for verifying compliance.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Server**: A single Apache web server instance
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

This repository demonstrates using Chef InSpec for compliance testing with Ansible playbooks. The main components are:

1. **website_https.yml** (Ansible Playbook):
   - Installs Apache 2.4.41 web server package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates SSL certificate directory at /etc/apache2/certs
   - Generates self-signed SSL certificates using OpenSSL
   - Configures Apache virtual host for HTTPS on port 443
   - Creates web content directory at /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default site and enables the new HTTPS site
   - Activates SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml** (Ansible Playbook):
   - Addresses SSL POODLE vulnerability by modifying Apache SSL configuration
   - Updates /etc/apache2/mods-available/ssl.conf to disable older protocols
   - Sets SSLProtocol to only allow TLSv1.2
   - Restarts Apache and SSH services after changes
   - Resources: replace, service

3. **tests/website_https_verify.rb** (InSpec Test):
   - Verifies port 443 is listening
   - Checks HTTPS response returns status 200
   - Confirms page content contains "Hello, world!"
   - Validates SSL3 protocol is disabled (security check)
   - Validates TLSv1.2 protocol is enabled
   - Resources: port, http, ssl

4. **tests/ssh_profile.rb** (InSpec Test):
   - Implements a security control to verify SSH root login is disabled
   - Checks /etc/ssh/sshd_config for PermitRootLogin setting
   - Includes STIG compliance information (SRG-OS-000112, V-38607)
   - Resources: sshd_config, package

5. **kitchen.yml** (Test Kitchen Configuration):
   - Configures test environment using Vagrant
   - Uses Ansible as the provisioner
   - Specifies Ubuntu 20.04 as the test platform
   - Runs InSpec tests to verify the configuration

## Dependencies

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

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module enabled

# SSL configuration
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol  # Should show '-all +TLSv1.2'

# Certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"
ls -la /etc/apache2/certs/  # Should show apache.key, apache.crt, apache.csr

# Virtual host configuration
ls -la /etc/apache2/sites-enabled/  # Should show helloworld.conf symlink
cat /etc/apache2/sites-available/helloworld.conf | grep -E 'VirtualHost|DocumentRoot|SSLEngine'

# Web content
ls -la /var/www/helloworld/
cat /var/www/helloworld/index.html  # Should contain "Hello, world!"

# HTTPS connectivity
curl -k https://localhost/  # Should return 200 OK with "Hello, world!" content
curl -I -k https://localhost/  # Should show HTTP/1.1 200 OK

# SSL protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost  # Should NOT show SSLv3
openssl s_client -connect localhost:443 -tls1_2  # Should succeed
openssl s_client -connect localhost:443 -ssl3  # Should fail

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache2
lsof -i :443
```