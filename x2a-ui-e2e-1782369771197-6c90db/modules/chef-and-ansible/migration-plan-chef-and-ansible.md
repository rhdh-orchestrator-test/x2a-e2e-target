---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not actually a Chef cookbook but an Ansible playbook with Chef InSpec tests. The module deploys an Apache web server with HTTPS enabled using a self-signed certificate and includes InSpec tests for compliance verification.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Server**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled with self-signed certificate, TLSv1.2 protocol

## File Structure

```
No Chef recipes found
No Chef providers found
No Chef templates found
No Chef attributes found
```

## Module Explanation

This is not a Chef cookbook but an Ansible playbook with Chef InSpec tests. The module consists of:

1. **website_https.yml** (Ansible playbook):
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates SSL certificate directory at /etc/apache2/certs
   - Generates self-signed SSL certificate using OpenSSL
   - Configures Apache virtual host for HTTPS
   - Deploys a simple "Hello World" website
   - Enables SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml** (Ansible playbook):
   - Secures Apache SSL configuration by disabling vulnerable protocols
   - Updates SSL configuration to only allow TLSv1.2
   - Resources: replace, service

3. **tests/website_https_verify.rb** (Chef InSpec test):
   - Verifies port 443 is listening
   - Checks HTTPS website returns 200 status and contains "Hello, world!"
   - Ensures SSL3 protocol is disabled
   - Ensures TLSv1.2 protocol is enabled

4. **tests/ssh_profile.rb** (Chef InSpec test):
   - Verifies SSH root login is disabled for security compliance
   - Includes STIG references and compliance metadata

## Dependencies

**External cookbook dependencies**: None (not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive. The SSL certificates are generated during deployment rather than being stored in the repository.

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
- Apache virtual host configuration (inline template in website_https.yml)
- HTML website content (inline template in website_https.yml)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Verify SSL module is enabled

# SSL certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout  # Check certificate details
openssl verify -CAfile /etc/apache2/certs/apache.crt /etc/apache2/certs/apache.crt  # Self-signed cert verification

# Website accessibility
curl -k https://localhost/  # Should return 200 OK with "Hello, world!" content
curl -I -k https://localhost/  # Should return HTTP/1.1 200 OK

# SSL protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost  # Should show TLSv1.2 enabled, SSLv3 disabled
openssl s_client -connect localhost:443 -tls1_2  # Should connect successfully
openssl s_client -connect localhost:443 -ssl3  # Should fail to connect

# Apache virtual host configuration
grep -r "DocumentRoot" /etc/apache2/sites-enabled/
ls -la /etc/apache2/sites-enabled/  # Should show helloworld.conf symlink
ls -la /etc/apache2/sites-available/  # Should show helloworld.conf file

# File permissions
ls -la /etc/apache2/certs/  # Check SSL certificate permissions
ls -la /var/www/helloworld/  # Check website directory permissions
ls -la /var/www/helloworld/index.html  # Check HTML file permissions

# SSL configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf  # Should show "SSLProtocol -all +TLSv1.2"

# Network listening
netstat -tulpn | grep :443  # Should show Apache listening on port 443
ss -tlnp | grep apache  # Should show Apache listening on port 443

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
journalctl -u apache2 -f
```