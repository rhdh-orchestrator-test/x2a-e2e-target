---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a Chef cookbook but a demonstration of using Chef InSpec for compliance testing with Ansible. The repository contains Ansible playbooks that set up an Apache web server with HTTPS and InSpec tests to verify compliance. No migration is needed as the implementation is already in Ansible.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Server**: 
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled with self-signed certificate

## File Structure

```
website_https.yml
poodle_fix.yml
tests/website_https_verify.rb
tests/ssh_profile.rb
kitchen.yml
README.md
index.html
```

## Module Explanation

The repository demonstrates using Chef InSpec for compliance testing with Ansible and contains the following components:

1. **website_https.yml** (Ansible Playbook):
   - Installs Apache 2.4.41 web server package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates: /etc/apache2/certs
   - Generates self-signed SSL certificate using OpenSSL
   - Configures Apache virtual host for HTTPS
   - Creates web content directory: /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml** (Ansible Playbook):
   - Addresses the POODLE vulnerability by updating SSL configuration
   - Modifies /etc/apache2/mods-available/ssl.conf to disable vulnerable protocols
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
   - Implements a security control to ensure SSH root login is disabled
   - Checks /etc/ssh/sshd_config for PermitRootLogin setting
   - Includes STIG compliance information (tags for SRG-OS-000112, V-38607)
   - Resources: sshd_config, package

5. **kitchen.yml** (Test Kitchen Configuration):
   - Configures Test Kitchen to use Vagrant as the driver
   - Sets up Ansible as the provisioner
   - Configures InSpec as the verifier
   - Specifies Ubuntu 20.04 as the test platform
   - Points to website_https.yml as the playbook to run
   - Points to tests/website_https_verify.rb as the test to run

## Dependencies

**External cookbook dependencies**: None (this is not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

No credentials or secrets were detected in this repository. All configuration values appear to be non-sensitive. The SSL certificates are generated during playbook execution and are not pre-existing secrets.

## Checks for the Migration

Since this is already implemented in Ansible, no migration is needed. However, here are the verification checks that would be important for this implementation:

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
- Apache virtual host configuration (rendered inline from variable)
- HTML content (rendered inline from variable)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
systemctl status sshd

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Verify SSL module is enabled

# SSL certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout  # Check certificate details
openssl verify -CAfile /etc/apache2/certs/apache.crt /etc/apache2/certs/apache.crt  # Self-signed cert verification

# Website accessibility
curl -k https://localhost/  # Should return HTML with "Hello, world!"
curl -I -k https://localhost/  # Should return HTTP 200

# SSL protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost  # Should show TLSv1.2 enabled, SSLv3 disabled

# Apache virtual host configuration
grep -r "DocumentRoot" /etc/apache2/sites-enabled/
ls -la /etc/apache2/sites-enabled/  # Should show helloworld.conf symlink
ls -la /etc/apache2/sites-available/  # Should show helloworld.conf file

# POODLE vulnerability check
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf  # Should show "SSLProtocol -all +TLSv1.2"

# SSH security check
grep "PermitRootLogin" /etc/ssh/sshd_config  # Should not be set to "yes"

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache
```