# Migration Plan: ansible-https-website

**TLDR**: This is already an Ansible playbook that configures an Apache web server with HTTPS support. It installs Apache, sets up SSL certificates, configures a virtual host, and deploys a simple "Hello World" website.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS site**: A single Apache web server instance with SSL/HTTPS enabled
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled with self-signed certificate

## File Structure

```
chef-and-ansible/website_https.yml
```

## Module Explanation

The Ansible playbook performs operations in this order:

1. **Package Installation**:
   - Updates apt cache
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs supporting packages: curl, openssl, python3-openssl
   - Resources: apt (2)

2. **SSL Certificate Setup**:
   - Creates directory for certificates at /etc/apache2/certs
   - Generates an OpenSSL private key at /etc/apache2/certs/apache.key
   - Generates a CSR at /etc/apache2/certs/apache.csr
   - Creates a self-signed certificate at /etc/apache2/certs/apache.crt
   - Resources: file (1), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1)

3. **Website Configuration**:
   - Creates virtual host configuration at /etc/apache2/sites-available/helloworld.conf
   - Creates website directory at /var/www/helloworld
   - Deploys index.html to /var/www/helloworld/index.html
   - Resources: copy (2), file (1)

4. **Apache Configuration**:
   - Disables default virtual host (000-default)
   - Enables the helloworld virtual host
   - Enables SSL module in Apache
   - Resources: command (3)

5. **Service Management**:
   - Restarts Apache service after configuration changes
   - Restarts SSH service after enabling SSL
   - Resources: service (2) via handlers

## Dependencies

**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.csr
- /etc/apache2/certs/apache.crt

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Virtual host configuration from variable `conftext` to /etc/apache2/sites-available/helloworld.conf
- Website content from variable `webtext` to /var/www/helloworld/index.html

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Configuration validation
apache2ctl -t
apache2ctl -M | grep ssl  # Verify SSL module is enabled
ls -la /etc/apache2/sites-enabled/  # Should show helloworld.conf symlink
ls -la /etc/apache2/sites-available/  # Should show helloworld.conf file
cat /etc/apache2/sites-available/helloworld.conf

# Certificate verification
ls -la /etc/apache2/certs/
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout  # View certificate details

# Website content
ls -la /var/www/helloworld/
cat /var/www/helloworld/index.html

# HTTPS connectivity
curl -k https://localhost/  # Should return the Hello World page
curl -I -k https://localhost/  # Should return HTTP 200 OK

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache

# SSL/TLS verification
openssl s_client -connect localhost:443 -servername myhost
```