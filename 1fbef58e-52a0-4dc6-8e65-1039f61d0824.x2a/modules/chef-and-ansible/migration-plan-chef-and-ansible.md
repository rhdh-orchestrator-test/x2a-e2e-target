---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing with Ansible playbooks. The repository contains Ansible playbooks that set up an Apache web server with HTTPS and InSpec tests to verify compliance.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Server**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled, TLSv1.2 only (SSLProtocol -all +TLSv1.2)

## File Structure

```
website_https.yml
poodle_fix.yml
tests/website_https_verify.rb
tests/ssh_profile.rb
kitchen.yml
index.html
README.md
```

## Module Explanation

This repository demonstrates using Chef InSpec for compliance testing with Ansible rather than being a traditional Chef cookbook. The main components are:

1. **website_https.yml** (Ansible Playbook):
   - Installs Apache 2.4.41-4ubuntu3.10 package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates at /etc/apache2/certs
   - Generates self-signed SSL certificate and key
   - Configures a virtual host for HTTPS on port 443
   - Creates a "Hello World" website at /var/www/helloworld
   - Disables the default site and enables the new virtual host
   - Enables SSL module in Apache
   - Resources: apt (3), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml** (Ansible Playbook):
   - Modifies Apache SSL configuration to disable vulnerable SSL protocols
   - Updates /etc/apache2/mods-available/ssl.conf to use only TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace (1), service (2)

3. **tests/website_https_verify.rb** (InSpec Test):
   - Verifies port 443 is listening
   - Checks HTTPS response returns status 200 and contains "Hello, world!"
   - Ensures SSL3 protocol is disabled
   - Ensures TLS 1.2 protocol is enabled

4. **tests/ssh_profile.rb** (InSpec Test):
   - Verifies SSH root login is disabled for security compliance
   - Checks /etc/ssh/sshd_config for PermitRootLogin setting

5. **kitchen.yml** (Test Kitchen Configuration):
   - Configures Test Kitchen to use Vagrant
   - Uses Ansible as the provisioner
   - Specifies website_https.yml as the playbook to run
   - Uses InSpec as the verifier with website_https_verify.rb test

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
- /etc/apache2/mods-available/ssl.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.crt
- /etc/apache2/certs/apache.csr

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Virtual host configuration rendered once to /etc/apache2/sites-available/helloworld.conf
- Website content rendered once to /var/www/helloworld/index.html

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module

# SSL configuration
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol
# Should show: SSLProtocol -all +TLSv1.2

# Virtual host configuration
cat /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/ | grep helloworld

# SSL certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout
openssl verify -CAfile /etc/apache2/certs/apache.crt /etc/apache2/certs/apache.crt

# Website content
cat /var/www/helloworld/index.html | grep "Hello, world!"

# HTTPS connectivity
curl -k https://localhost/ | grep "Hello, world!"
curl -I -k https://localhost/  # Should return HTTP/1.1 200 OK

# SSL/TLS protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost
# Should show TLSv1.2 enabled and SSLv3 disabled

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache

# SSH configuration (related to the InSpec test)
cat /etc/ssh/sshd_config | grep PermitRootLogin
# Should NOT show: PermitRootLogin yes
```