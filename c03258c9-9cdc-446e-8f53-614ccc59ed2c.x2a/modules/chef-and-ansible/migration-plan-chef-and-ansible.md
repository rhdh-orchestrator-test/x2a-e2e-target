# Migration Plan: chef-and-ansible

**TLDR**: This repository demonstrates how to use Chef InSpec for compliance testing alongside Ansible playbooks. It contains Ansible playbooks for setting up a secure HTTPS website and fixing SSL vulnerabilities, along with InSpec tests to verify compliance.

## Service Type and Instances

**Service Type**: Web Server (Apache with HTTPS)

**Configured Instances**:
- **Apache HTTPS Server**: Serves a simple "Hello World" website over HTTPS
  - Location/Path: /etc/apache2 or /etc/httpd (depending on distribution)
  - Port/Socket: 443
  - Key Config: SSL/TLS configuration with TLSv1.2 enabled

## File Structure

```
.
├── README.md
├── kitchen.yml
├── poodle_fix.yml
├── tests
│   ├── ssh_profile.rb
│   └── website_https_verify.rb
└── website_https.yml
```

## Module Explanation

The repository performs operations in this order:

1. **website_https.yml** (`website_https.yml`):
   - Installs Apache, curl, openssl, and PyOpenSSL packages
   - Creates directories for SSL certificates
   - Generates a self-signed SSL certificate
   - Configures an Apache virtual host for HTTPS
   - Deploys a simple "Hello World" website
   - Enables SSL in Apache
   - Restarts Apache and SSH services

2. **poodle_fix.yml** (`poodle_fix.yml`):
   - Updates the Apache SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Restarts Apache and SSH services

3. **InSpec Tests** (`tests/website_https_verify.rb` and `tests/ssh_profile.rb`):
   - Verifies that port 443 is listening
   - Checks that the website returns a 200 status code and contains "Hello, world!"
   - Confirms that vulnerable SSL protocols are disabled and TLSv1.2 is enabled
   - Verifies that SSH root login is disabled (security compliance check)

## Dependencies

**External cookbook dependencies**: None (uses Ansible, not Chef cookbooks)
**System package dependencies**: apache2/httpd, curl, openssl, python-pyopenssl/python3-pyopenssl
**Service dependencies**: apache2/httpd, ssh

## Checks for the Migration

**Files to verify**: 
- /etc/apache2/sites-available/default-ssl.conf or /etc/httpd/conf.d/ssl.conf
- /etc/ssl/certs/apache-selfsigned.crt
- /etc/ssl/private/apache-selfsigned.key
- /var/www/html/index.html

**Service endpoints to check**: 
- https://localhost:443

**Templates rendered**: None (uses Ansible templates)

## Pre-flight checks:
```bash
# Service status commands
systemctl status apache2  # or httpd on RHEL/CentOS
systemctl status sshd

# Apache HTTPS Server checks
curl -k https://localhost:443
openssl s_client -connect localhost:443 -tls1_2
openssl s_client -connect localhost:443 -ssl3 # Should fail
grep -r "SSLProtocol" /etc/apache2/ # or /etc/httpd/
grep -r "Hello, world" /var/www/html/index.html

# Configuration validation commands
apache2ctl -t  # or httpd -t on RHEL/CentOS
ls -la /etc/ssl/certs/apache-selfsigned.crt
ls -la /etc/ssl/private/apache-selfsigned.key

# Network/connectivity checks
netstat -tulpn | grep :443
ss -tulpn | grep :443
```