---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not actually a Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing with Ansible playbooks. The repository contains Ansible playbooks for configuring a secure HTTPS website with Apache and InSpec tests for verifying compliance.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Server**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled with self-signed certificate, TLS 1.2 enforced

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

The repository demonstrates using Chef InSpec for compliance testing with Ansible playbooks:

1. **website_https.yml**:
   - Installs Apache 2.4.41 web server package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates SSL certificate directory at /etc/apache2/certs
   - Generates self-signed SSL certificate using OpenSSL
   - Configures Apache virtual host for HTTPS on port 443
   - Deploys a simple "Hello World" website to /var/www/helloworld
   - Disables default site and enables the new HTTPS site
   - Enables SSL module in Apache
   - Resources: apt (3), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml**:
   - Modifies Apache SSL configuration to disable vulnerable SSL protocols
   - Updates /etc/apache2/mods-available/ssl.conf to enforce TLS 1.2 only
   - Disables all other SSL/TLS protocols to mitigate POODLE vulnerability
   - Resources: replace (1), service (2)

3. **tests/website_https_verify.rb** (InSpec test):
   - Verifies port 443 is listening
   - Checks HTTPS website returns 200 status code
   - Confirms website content contains "Hello, world!"
   - Validates SSL3 protocol is disabled (security check)
   - Validates TLS 1.2 protocol is enabled
   - Resources: port (1), http (1), ssl (2)

4. **tests/ssh_profile.rb** (InSpec test):
   - Implements a security control to verify SSH root login is disabled
   - Checks /etc/ssh/sshd_config for PermitRootLogin setting
   - Includes STIG compliance information (SRG-OS-000112, V-38607)
   - Resources: sshd_config (1), package (1)

5. **kitchen.yml**:
   - Configures Test Kitchen to use Vagrant driver
   - Sets up Ansible as the provisioner
   - Configures InSpec as the verifier
   - Uses Ubuntu 20.04 as the test platform
   - Runs website_https.yml playbook for provisioning
   - Executes website_https_verify.rb for verification

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
- HTML website content (inline template → /var/www/helloworld/index.html)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module enabled

# SSL configuration
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol
# Should show: SSLProtocol -all +TLSv1.2

# Virtual host configuration
cat /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/ | grep helloworld

# Certificate verification
ls -la /etc/apache2/certs/
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"
openssl verify -CAfile /etc/apache2/certs/apache.crt /etc/apache2/certs/apache.crt

# Website accessibility
curl -k https://localhost/ | grep "Hello, world!"
curl -I -k https://localhost/  # Should return HTTP/1.1 200 OK

# SSL/TLS protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost
# Should NOT show SSLv3 as supported
# Should show TLSv1.2 as supported

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# SSH security check (from InSpec test)
grep PermitRootLogin /etc/ssh/sshd_config
# Should NOT show "PermitRootLogin yes"
```