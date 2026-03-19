# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing alongside Ansible. The repository contains Ansible playbooks for configuring a secure Apache web server with HTTPS and InSpec tests for verifying compliance.

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

This repository demonstrates using Chef InSpec for compliance testing alongside Ansible deployments. It does not contain Chef recipes but rather Ansible playbooks with InSpec tests.

1. **website_https.yml** (`chef-and-ansible/website_https.yml`):
   - Installs Apache 2.4.41 web server package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates: /etc/apache2/certs
   - Generates self-signed SSL certificate using OpenSSL
   - Configures Apache virtual host for HTTPS on port 443
   - Deploys a simple "Hello World" HTML page
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Resources: apt (3), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml** (`chef-and-ansible/poodle_fix.yml`):
   - Addresses the POODLE vulnerability by restricting SSL protocols
   - Modifies /etc/apache2/mods-available/ssl.conf to only allow TLSv1.2
   - Disables older SSL protocols
   - Restarts Apache and SSH services after changes
   - Resources: replace (1), service (2)

3. **InSpec Tests**:
   - **website_https_verify.rb** (`chef-and-ansible/tests/website_https_verify.rb`):
     - Verifies port 443 is listening
     - Checks HTTPS response returns status 200
     - Confirms page content contains "Hello, world!"
     - Validates SSL3 protocol is disabled
     - Validates TLSv1.2 protocol is enabled
   
   - **ssh_profile.rb** (`chef-and-ansible/tests/ssh_profile.rb`):
     - Compliance check for SSH security
     - Verifies root login is disabled in SSH configuration
     - Includes security rationale and STIG references

4. **Test Kitchen Configuration** (`chef-and-ansible/kitchen.yml`):
   - Configures Vagrant as the driver
   - Uses Ansible as the provisioner
   - Specifies InSpec as the verifier
   - Targets Ubuntu 20.04 platform
   - Runs website_https.yml playbook
   - Executes website_https_verify.rb tests

## Dependencies

**External cookbook dependencies**: None (this is not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl, openssh-server
**Service dependencies**: apache2, sshd

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /etc/apache2/sites-enabled/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.csr
- /etc/apache2/certs/apache.crt
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (*)

**Templates rendered**:
- None (direct content insertion via Ansible copy module)

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
openssl verify -CAfile /etc/apache2/certs/apache.crt /etc/apache2/certs/apache.crt

# SSL protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost
openssl s_client -connect localhost:443 -tls1_2
# Should succeed
openssl s_client -connect localhost:443 -ssl3
# Should fail with "ssl handshake failure"

# Web content verification
curl -k https://localhost/
curl -k https://localhost/ | grep "Hello, world!"

# POODLE fix verification
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf
# Should show: SSLProtocol -all +TLSv1.2

# SSH security verification
grep "PermitRootLogin" /etc/ssh/sshd_config
# Should NOT show "PermitRootLogin yes"

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache
lsof -i :443

# Log verification
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```