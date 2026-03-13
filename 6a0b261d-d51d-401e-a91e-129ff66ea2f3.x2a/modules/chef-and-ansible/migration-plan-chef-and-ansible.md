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
chef-and-ansible/website_https.yml
chef-and-ansible/poodle_fix.yml
chef-and-ansible/tests/website_https_verify.rb
chef-and-ansible/tests/ssh_profile.rb
chef-and-ansible/kitchen.yml
chef-and-ansible/index.html
```

## Module Explanation

This repository demonstrates using Chef InSpec for compliance testing with Ansible rather than being a Chef cookbook to migrate. The main components are:

1. **website_https.yml** (`chef-and-ansible/website_https.yml`):
   - Installs Apache 2.4.41 web server package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates certificate directory at /etc/apache2/certs
   - Generates self-signed SSL certificate using OpenSSL
   - Configures Apache virtual host for HTTPS on port 443
   - Deploys a simple "Hello World" HTML page
   - Enables SSL module in Apache
   - Resources: apt (3), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml** (`chef-and-ansible/poodle_fix.yml`):
   - Addresses SSL POODLE vulnerability by restricting protocols
   - Modifies /etc/apache2/mods-available/ssl.conf to only allow TLSv1.2
   - Disables older SSL protocols
   - Resources: replace (1), service (2)

3. **InSpec Tests**:
   - **website_https_verify.rb** (`chef-and-ansible/tests/website_https_verify.rb`):
     - Verifies port 443 is listening
     - Checks HTTPS response returns 200 status code
     - Confirms page content contains "Hello, world!"
     - Validates SSL3 is disabled and TLSv1.2 is enabled
   
   - **ssh_profile.rb** (`chef-and-ansible/tests/ssh_profile.rb`):
     - Compliance check for SSH root login being disabled
     - Includes security rationale and STIG references
     - Verifies PermitRootLogin is not set to 'yes' in sshd_config

4. **Test Kitchen Configuration** (`chef-and-ansible/kitchen.yml`):
   - Configures Vagrant as the test driver
   - Uses Ansible as the provisioner
   - Specifies InSpec as the verifier
   - Targets Ubuntu 20.04 platform
   - References website_https.yml as the playbook to test
   - Points to website_https_verify.rb for verification tests

## Dependencies

**External cookbook dependencies**: None (this is not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl, openssh-server
**Service dependencies**: apache2, sshd

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.csr
- /etc/apache2/certs/apache.crt
- /var/www/helloworld/index.html
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (*:443)

**Templates rendered**:
- Apache virtual host configuration (inline template in website_https.yml)
- HTML content (inline template in website_https.yml)

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

# SSL Certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout
openssl verify -CAfile /etc/apache2/certs/apache.crt /etc/apache2/certs/apache.crt

# SSL Protocol verification
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol
openssl s_client -connect localhost:443 -tls1_2
# Should succeed
openssl s_client -connect localhost:443 -ssl3
# Should fail with "wrong version number" or similar

# Web content verification
curl -k https://localhost/
curl -k https://localhost/ | grep "Hello, world!"

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache2
lsof -i :443

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# SSH configuration (for compliance)
cat /etc/ssh/sshd_config | grep PermitRootLogin
sshd -T | grep permitrootlogin

# Run InSpec tests directly
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```