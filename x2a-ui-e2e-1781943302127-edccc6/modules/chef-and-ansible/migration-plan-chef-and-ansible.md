---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather an example of using Chef InSpec with Ansible. The module contains Ansible playbooks for configuring an Apache web server with HTTPS and SSL security fixes, along with InSpec tests for validation.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Server**: 
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled with self-signed certificate, TLSv1.2 protocol

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

The module contains Ansible playbooks that perform operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache 2.4.41-4ubuntu3.10 package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates at /etc/apache2/certs
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web root directory at /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default virtual host and enables the new one
   - Enables SSL module in Apache
   - Resources: apt (2), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Sets SSLProtocol to "-all +TLSv1.2" to only allow TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace (1), service (2)

3. **Tests**:
   - **tests/website_https_verify.rb**: InSpec tests to verify:
     - Port 443 is listening
     - HTTPS site returns 200 status and contains "Hello, world!"
     - SSL3 protocol is disabled
     - TLS1.2 protocol is enabled
   
   - **tests/ssh_profile.rb**: InSpec test to verify:
     - SSH root login is disabled (security compliance check)

## Dependencies

**External cookbook dependencies**: None (this is an Ansible playbook with InSpec tests)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive. The SSL certificates are generated during playbook execution rather than being stored in the repository.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.csr
- /etc/apache2/certs/apache.crt
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Apache virtual host configuration (inline template in website_https.yml)
- HTML content (inline template in website_https.yml)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
systemctl status sshd

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module

# Virtual host configuration
cat /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/  # Should show helloworld.conf symlink
ls -la /etc/apache2/sites-enabled/000-default.conf  # Should NOT exist

# SSL configuration
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol  # Should show "SSLProtocol -all +TLSv1.2"
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout  # Check certificate details

# Website content
cat /var/www/helloworld/index.html  # Should contain "Hello, world!"

# Directory permissions
ls -la /var/www/helloworld/  # Should be mode 0755
ls -la /etc/apache2/certs/  # Should be mode 0640

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache

# HTTPS connectivity
curl -k https://localhost/  # Should return 200 OK with "Hello, world!"
curl -k -v https://localhost/ 2>&1 | grep "TLS"  # Should show TLSv1.2

# SSL security verification
nmap --script ssl-enum-ciphers -p 443 localhost  # Should NOT show SSLv3
openssl s_client -connect localhost:443 -ssl3 2>&1  # Should fail
openssl s_client -connect localhost:443 -tls1_2 2>&1  # Should succeed

# SSH security check
grep PermitRootLogin /etc/ssh/sshd_config  # Should NOT be "yes"
```