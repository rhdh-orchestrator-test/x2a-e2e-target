---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a Chef cookbook to migrate, but rather a demonstration of using Chef InSpec for compliance testing with Ansible. The repository contains Ansible playbooks for setting up an HTTPS website with Apache and InSpec tests to verify compliance.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Website**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: TLS 1.2 enabled, SSL3 disabled, self-signed certificate

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

This is not a Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing alongside Ansible. The repository contains:

1. **website_https.yml** (Ansible playbook):
   - Installs Apache 2.4.41 web server
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates SSL certificate directory: /etc/apache2/certs
   - Generates self-signed SSL certificate and key
   - Configures Apache virtual host for HTTPS
   - Creates website directory: /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Enables SSL module in Apache
   - Disables default site and enables custom site
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml** (Ansible playbook):
   - Modifies Apache SSL configuration to disable vulnerable protocols
   - Updates /etc/apache2/mods-available/ssl.conf to only allow TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace, service

3. **tests/website_https_verify.rb** (InSpec test):
   - Verifies port 443 is listening
   - Checks HTTPS website returns 200 status code
   - Confirms website content contains "Hello, world!"
   - Verifies SSL3 protocol is disabled
   - Verifies TLS 1.2 protocol is enabled

4. **tests/ssh_profile.rb** (InSpec test):
   - Compliance test for SSH configuration
   - Verifies root login is disabled in SSH
   - Includes security rationale and impact assessment
   - Tagged with security identifiers (SRG, CCI, etc.)

5. **kitchen.yml** (Test Kitchen configuration):
   - Configures Vagrant as the driver
   - Sets up Ansible as the provisioner
   - Configures InSpec as the verifier
   - Uses Ubuntu 20.04 as the test platform
   - Points to the website_https.yml playbook for provisioning
   - References the website_https_verify.rb test for verification

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

No credentials or secrets were detected in this repository. All configuration values appear to be non-sensitive. The SSL certificates are generated during playbook execution and are not pre-stored.

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
- None (using Ansible copy module with inline content)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module enabled

# SSL configuration
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol  # Should show "SSLProtocol -all +TLSv1.2"

# Certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"  # Should show CN=myhost
ls -la /etc/apache2/certs/  # Should show apache.key, apache.crt, apache.csr

# Website content
cat /var/www/helloworld/index.html  # Should contain "Hello, world!"
cat /etc/apache2/sites-available/helloworld.conf  # Should show VirtualHost config for port 443

# Site availability
curl -k https://localhost/  # Should return 200 OK with "Hello, world!" content
curl -I -k https://localhost/  # Should show HTTP/1.1 200 OK

# SSL/TLS protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost  # Should show TLSv1.2 enabled, no SSLv3

# Virtual host configuration
ls -la /etc/apache2/sites-enabled/  # Should show helloworld.conf symlink
ls -la /etc/apache2/sites-available/  # Should show helloworld.conf file

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache
lsof -i :443
```