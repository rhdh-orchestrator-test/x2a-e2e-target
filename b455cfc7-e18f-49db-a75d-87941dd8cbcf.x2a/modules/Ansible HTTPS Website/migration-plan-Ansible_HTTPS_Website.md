# Analysis: Ansible HTTPS Website Playbook

**TLDR**: This is an Ansible playbook that sets up an Apache web server with HTTPS enabled, using a self-signed certificate. It deploys a simple "Hello World" website and configures Apache to serve it over HTTPS on port 443.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Website**: 
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
   - Resources: apt module (2)

2. **SSL Certificate Setup**:
   - Creates directory for certificates at /etc/apache2/certs
   - Generates an OpenSSL private key at /etc/apache2/certs/apache.key
   - Generates a CSR (Certificate Signing Request) at /etc/apache2/certs/apache.csr
   - Creates a self-signed certificate at /etc/apache2/certs/apache.crt
   - Resources: file module (1), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1)

3. **Apache Configuration**:
   - Creates Apache virtual host configuration at /etc/apache2/sites-available/helloworld.conf
   - Creates website directory at /var/www/helloworld
   - Deploys index.html to /var/www/helloworld/index.html
   - Disables default virtual host (000-default)
   - Enables the new virtual host (helloworld)
   - Enables SSL module in Apache
   - Resources: copy module (2), file module (1), command module (3)

4. **Service Management**:
   - Restarts Apache service when configuration changes
   - Restarts SSH service when SSL is enabled
   - Resources: service module (2) via handlers

## Dependencies

**System package dependencies**: 
- apache2 (version 2.4.41-4ubuntu3.10)
- curl
- openssl
- python3-openssl

**Service dependencies**: 
- apache2 service
- sshd service

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.csr
- /etc/apache2/certs/apache.crt

**Service endpoints to check**:
- Port listening: 443 (HTTPS)
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
apache2ctl -M | grep ssl  # Should show ssl_module

# SSL certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout
openssl verify -CAfile /etc/apache2/certs/apache.crt /etc/apache2/certs/apache.crt

# Website accessibility
curl -k https://localhost/
curl -k https://localhost/ | grep "Hello, world!"

# Virtual host configuration
cat /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/  # Should show helloworld.conf symlink
ls -la /etc/apache2/sites-enabled/  # Should NOT show 000-default.conf symlink

# File permissions
ls -la /etc/apache2/certs/
ls -la /var/www/helloworld/

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache2
lsof -i :443
```