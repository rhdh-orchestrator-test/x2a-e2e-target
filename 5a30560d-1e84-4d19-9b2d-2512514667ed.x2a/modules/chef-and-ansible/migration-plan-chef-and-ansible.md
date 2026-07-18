---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather an example of using Chef InSpec with Ansible. The module contains Ansible playbooks for configuring an Apache web server with HTTPS and SSL security fixes, along with InSpec tests for validation. No actual Chef recipes exist in this module.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Server**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: TLS 1.2 enabled, SSL3 disabled, self-signed certificate

## File Structure

```
No Chef recipes found in this module
No Chef providers found in this module
No Chef templates found in this module
No Chef attribute files found in this module
```

## Module Explanation

This module is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec with Ansible. The module contains:

1. **Ansible Playbooks**:
   - `website_https.yml`: Sets up an Apache web server with HTTPS
     - Installs Apache 2.4.41-4ubuntu3.10
     - Installs curl, openssl, and python3-openssl
     - Creates SSL certificates directory
     - Generates self-signed SSL certificates
     - Configures a virtual host for HTTPS
     - Deploys a simple "Hello World" website
     - Enables SSL module
     - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

   - `poodle_fix.yml`: Fixes SSL security vulnerabilities
     - Updates SSL configuration to disable vulnerable protocols
     - Enables only TLS 1.2
     - Resources: replace, service

2. **Test Files**:
   - `tests/website_https_verify.rb`: InSpec tests to verify:
     - Port 443 is listening
     - HTTPS website returns 200 status and contains "Hello, world!"
     - SSL3 protocol is disabled
     - TLS 1.2 protocol is enabled

   - `tests/ssh_profile.rb`: InSpec tests to verify:
     - SSH root login is disabled (security compliance check)

3. **Configuration**:
   - `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
     - Uses Vagrant driver
     - Targets Ubuntu 20.04
     - Runs website_https.yml playbook
     - Verifies with InSpec tests

## Dependencies

**External cookbook dependencies**: None (not a Chef cookbook)
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
- No Chef templates, but Ansible templates for:
  - Apache virtual host configuration (rendered once)
  - Website HTML content (rendered once)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Apache configuration validation
apache2ctl -t
apache2ctl -M | grep ssl

# SSL configuration
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol
openssl s_client -connect localhost:443 -tls1_2 </dev/null
openssl s_client -connect localhost:443 -ssl3 </dev/null 2>&1 | grep "Protocol version"

# Website availability
curl -k https://localhost/ | grep "Hello, world!"
curl -I -k https://localhost/

# Certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"
ls -la /etc/apache2/certs/

# Virtual host configuration
cat /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/ | grep helloworld

# SSH security (related to the InSpec test)
cat /etc/ssh/sshd_config | grep PermitRootLogin
systemctl status sshd

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
journalctl -u apache2 -f
```