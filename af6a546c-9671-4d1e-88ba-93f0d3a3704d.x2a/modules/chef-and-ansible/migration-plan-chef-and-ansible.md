---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This repository demonstrates using Chef InSpec for compliance testing with Ansible playbooks. It contains Ansible playbooks that set up an HTTPS website with Apache and SSL configuration, along with InSpec tests to verify the configuration meets security requirements.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS server**: A single Apache web server instance configured with SSL/TLS
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled, TLSv1.2 protocol, self-signed certificate

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

This repository demonstrates using Chef InSpec for compliance testing with Ansible rather than being a Chef cookbook to migrate. The components work together as follows:

1. **website_https.yml** (Ansible playbook):
   - Installs Apache 2.4.41 web server package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates at /etc/apache2/certs
   - Generates self-signed SSL certificate (key, CSR, and certificate)
   - Configures Apache virtual host for HTTPS on port 443
   - Creates website content directory at /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Resources: apt (3), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml** (Ansible playbook):
   - Addresses the POODLE vulnerability by restricting SSL/TLS protocols
   - Updates Apache SSL configuration to only allow TLSv1.2
   - Disables older, vulnerable protocols
   - Resources: replace (1), service (2)

3. **tests/website_https_verify.rb** (InSpec test):
   - Verifies port 443 is listening
   - Checks HTTPS website returns 200 status code
   - Confirms page content contains "Hello, world!"
   - Validates SSL3 protocol is disabled (security check)
   - Validates TLSv1.2 protocol is enabled

4. **tests/ssh_profile.rb** (InSpec test):
   - Security compliance test for SSH configuration
   - Verifies root login is disabled via SSH
   - Includes security rationale and compliance metadata (STIG IDs, CCI numbers)

5. **kitchen.yml** (Test Kitchen configuration):
   - Configures Test Kitchen to use Vagrant as the driver
   - Sets up Ansible as the provisioner
   - Configures InSpec as the verifier
   - Specifies Ubuntu 20.04 as the test platform
   - Links the website_https.yml playbook and website_https_verify.rb test

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

No credentials or secrets were detected in this repository. All configuration values appear to be non-sensitive. The SSL certificates are generated during playbook execution rather than being stored in the repository.

## Checks for the Migration

Since this is already an Ansible implementation with InSpec tests, no migration is needed. However, here are the verification checks that would be appropriate for this configuration:

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
- Apache virtual host configuration (rendered from variable)
- HTML content (rendered from variable)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
systemctl status sshd

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Verify SSL module is enabled

# SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2  # Should connect successfully
openssl s_client -connect localhost:443 -ssl3    # Should fail (protocol disabled)

# Website accessibility
curl -k https://localhost/  # Should return 200 OK with "Hello, world!" content
curl -k -I https://localhost/  # Should show HTTP/1.1 200 OK

# Virtual host configuration
grep -r "SSLEngine on" /etc/apache2/sites-enabled/
grep -r "DocumentRoot" /etc/apache2/sites-enabled/

# SSL protocol configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf  # Should show "-all +TLSv1.2"

# SSH security configuration
grep "PermitRootLogin" /etc/ssh/sshd_config  # Should not be set to "yes"

# Certificate verification
ls -la /etc/apache2/certs/
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
```