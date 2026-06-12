---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing alongside Ansible. The module contains Ansible playbooks for deploying an Apache web server with HTTPS and InSpec tests for verifying compliance.

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

The module demonstrates using Chef InSpec for compliance testing with Ansible deployments:

1. **website_https.yml**:
   - Installs Apache 2.4.41 web server package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates SSL certificate directory at /etc/apache2/certs
   - Generates self-signed SSL certificate using OpenSSL
   - Configures Apache virtual host for HTTPS
   - Creates web content directory at /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Enables SSL module in Apache
   - Disables default site and enables custom virtual host
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml**:
   - Modifies Apache SSL configuration to disable vulnerable protocols
   - Updates /etc/apache2/mods-available/ssl.conf to only allow TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace, service

3. **InSpec Tests**:
   - **tests/website_https_verify.rb**: Verifies HTTPS configuration
     - Checks port 443 is listening
     - Verifies HTTPS response contains "Hello, world!"
     - Ensures SSL3 protocol is disabled
     - Ensures TLS1.2 protocol is enabled
   
   - **tests/ssh_profile.rb**: Verifies SSH security compliance
     - Checks that SSH root login is disabled
     - Implements STIG control for SSH security

4. **kitchen.yml**:
   - Configures test-kitchen to use Vagrant
   - Uses Ansible as the provisioner
   - Runs the website_https.yml playbook
   - Uses InSpec for verification
   - Tests on Ubuntu 20.04

## Dependencies

**External cookbook dependencies**: None (this is not a traditional Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

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
- Apache virtual host configuration (rendered once)
- HTML content (rendered once)

## Pre-flight checks:

```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module enabled

# SSL configuration
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol  # Should show "SSLProtocol -all +TLSv1.2"

# Virtual host configuration
cat /etc/apache2/sites-available/helloworld.conf
ls -l /etc/apache2/sites-enabled/  # Should show helloworld.conf symlink
ls -l /etc/apache2/sites-enabled/000-default.conf  # Should NOT exist

# SSL certificate verification
ls -la /etc/apache2/certs/
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"  # Should show CN=myhost

# Website content
cat /var/www/helloworld/index.html  # Should contain "Hello, world!"

# HTTPS connectivity
curl -k https://localhost/  # Should return 200 OK with "Hello, world!" content
curl -I -k https://localhost/  # Should show HTTP/1.1 200 OK

# SSL protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost  # Should NOT show SSLv3
openssl s_client -connect localhost:443 -tls1_2  # Should succeed
openssl s_client -connect localhost:443 -ssl3  # Should fail

# SSH security check (from ssh_profile.rb)
grep PermitRootLogin /etc/ssh/sshd_config  # Should NOT be "yes"

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
```