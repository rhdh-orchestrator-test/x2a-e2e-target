---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing with Ansible. The repository contains Ansible playbooks for configuring an Apache web server with HTTPS and SSL security fixes, along with InSpec tests to verify the configuration.

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

The repository contains Ansible playbooks that perform operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates: /etc/apache2/certs
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web root directory: /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Resources: apt (3), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml**:
   - Modifies Apache SSL configuration to disable vulnerable protocols
   - Updates /etc/apache2/mods-available/ssl.conf to use only TLSv1.2
   - Resources: replace (1), service (2)

3. **InSpec Tests**:
   - **tests/website_https_verify.rb**: Verifies that:
     - Port 443 is listening
     - HTTPS site returns 200 status code
     - Response body contains "Hello, world!"
     - SSL3 protocol is disabled
     - TLS 1.2 protocol is enabled
   
   - **tests/ssh_profile.rb**: Verifies that:
     - SSH root login is disabled (PermitRootLogin is not set to 'yes')
     - Implements security requirements based on specific compliance standards (SRG-OS-000112, V-38607)

## Dependencies

**External cookbook dependencies**: None (This is not a Chef cookbook)
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
systemctl status sshd

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module

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

# Website content
cat /var/www/helloworld/index.html
grep "Hello, world!" /var/www/helloworld/index.html

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache

# HTTPS connectivity
curl -k https://localhost/ | grep "Hello, world!"

# SSL protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost
# Should NOT show SSLv3
# Should show TLSv1.2

# SSH configuration
grep PermitRootLogin /etc/ssh/sshd_config
# Should NOT be set to 'yes'

# Run InSpec tests (if InSpec is installed)
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```