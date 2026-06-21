---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing alongside Ansible. The module contains Ansible playbooks that set up an Apache web server with HTTPS and SSL security configurations, along with InSpec tests to verify compliance.

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

The module demonstrates using Chef InSpec for compliance testing with Ansible deployments. It contains:

1. **website_https.yml** (Ansible playbook):
   - Installs Apache 2.4.41 web server package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates at /etc/apache2/certs
   - Generates self-signed SSL certificate using OpenSSL
   - Configures Apache virtual host for HTTPS on port 443
   - Deploys a simple "Hello World" HTML page
   - Disables default site and enables the new HTTPS site
   - Enables SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml** (Ansible playbook):
   - Addresses SSL POODLE vulnerability by restricting protocols
   - Updates Apache SSL configuration to only allow TLSv1.2
   - Disables older, vulnerable SSL/TLS protocols
   - Restarts Apache and SSH services after changes
   - Resources: replace, service

3. **tests/website_https_verify.rb** (InSpec test):
   - Verifies port 443 is listening
   - Checks HTTPS website returns 200 status code
   - Confirms "Hello, world!" text appears in the response
   - Validates SSL3 protocol is disabled (security check)
   - Validates TLSv1.2 protocol is enabled
   - Resources: port, http, ssl

4. **tests/ssh_profile.rb** (InSpec test):
   - Implements a security control to verify SSH root login is disabled
   - Checks /etc/ssh/sshd_config for proper PermitRootLogin setting
   - Includes security metadata (STIG IDs, CCI references, etc.)
   - Resources: sshd_config, package

5. **kitchen.yml** (Test Kitchen configuration):
   - Configures test environment using Vagrant
   - Uses Ansible as the provisioner
   - Specifies Ubuntu 20.04 as the test platform
   - Runs InSpec tests to verify the deployment

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

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive. The SSL certificates are generated during deployment rather than being stored in the repository.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.crt
- /etc/apache2/certs/apache.csr
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
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
apache2ctl -M | grep ssl  # Should show ssl_module

# SSL certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"
openssl verify -CAfile /etc/apache2/certs/apache.crt /etc/apache2/certs/apache.crt

# SSL protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost
openssl s_client -connect localhost:443 -tls1_2
# Should succeed
openssl s_client -connect localhost:443 -ssl3
# Should fail with "protocol version not supported"

# Website accessibility
curl -k https://localhost/
curl -k -s https://localhost/ | grep "Hello, world!"

# Security configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf
# Should show: SSLProtocol -all +TLSv1.2

# SSH security check
grep "PermitRootLogin" /etc/ssh/sshd_config
# Should NOT show: PermitRootLogin yes

# Virtual host configuration
ls -la /etc/apache2/sites-enabled/
cat /etc/apache2/sites-available/helloworld.conf

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache
lsof -i :443
```