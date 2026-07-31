---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not actually a Chef cookbook but an Ansible playbook with Chef InSpec tests. The module deploys an Apache web server with HTTPS enabled using a self-signed certificate, and includes InSpec tests to verify compliance with security standards.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **Apache HTTPS Server**: A single Apache web server instance with HTTPS enabled
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443
  - Key Config: Uses self-signed SSL certificate, TLSv1.2 protocol only

## File Structure

```
No Chef recipes found
No Chef providers found
No Chef templates found
No Chef attributes found
```

## Module Explanation

This is not a Chef cookbook but an Ansible playbook with Chef InSpec tests. The module consists of:

1. **website_https.yml**: An Ansible playbook that:
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs curl, openssl, and python3-openssl
   - Creates a directory for SSL certificates
   - Generates a self-signed SSL certificate
   - Configures an HTTPS virtual host
   - Deploys a simple "Hello World" website
   - Enables SSL module in Apache
   - Disables the default site and enables the new virtual host
   - Restarts Apache and SSH services

2. **poodle_fix.yml**: An Ansible playbook that:
   - Updates the Apache SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2
   - Restarts Apache and SSH services

3. **tests/website_https_verify.rb**: A Chef InSpec test that:
   - Verifies port 443 is listening
   - Checks that the HTTPS site returns a 200 status code
   - Confirms the page contains "Hello, world!"
   - Ensures SSL3 protocol is disabled
   - Ensures TLSv1.2 protocol is enabled

4. **tests/ssh_profile.rb**: A Chef InSpec test that:
   - Verifies SSH root login is disabled for security compliance

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive.

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
- No templates are used; content is directly provided via variables in the playbook

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Web server connectivity
curl -k https://localhost/
curl -k -I https://localhost/

# SSL configuration
openssl s_client -connect localhost:443 -tls1_2
openssl s_client -connect localhost:443 -ssl3 || echo "SSL3 correctly disabled"

# Configuration validation
grep -E "SSLProtocol" /etc/apache2/mods-available/ssl.conf
apache2ctl -t
apache2ctl -M | grep ssl

# Certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"
ls -la /etc/apache2/certs/

# Virtual host configuration
cat /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/

# Website content
cat /var/www/helloworld/index.html
ls -la /var/www/helloworld/

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache
lsof -i :443

# SSH security (tested by InSpec)
grep "PermitRootLogin" /etc/ssh/sshd_config
```