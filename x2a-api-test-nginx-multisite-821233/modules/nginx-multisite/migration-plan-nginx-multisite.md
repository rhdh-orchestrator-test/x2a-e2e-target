---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Multi-site Nginx web server cookbook that configures 3 SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) with comprehensive security hardening including fail2ban, UFW firewall, SSH restrictions, and kernel security parameters.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:
- **test.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/test
  - Port/Socket: 80 (HTTP), 443 (HTTPS)
  - Key Config: SSL certificate, document root with index.html

- **ci.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/ci
  - Port/Socket: 80 (HTTP), 443 (HTTPS)
  - Key Config: SSL certificate, document root with index.html

- **status.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/status
  - Port/Socket: 80 (HTTP), 443 (HTTPS)
  - Key Config: SSL certificate, document root with index.html

## File Structure

```
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
cookbooks/nginx-multisite/attributes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Orchestrates the complete setup by including all sub-recipes
   - Resources: include_recipe (4)

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs security packages: fail2ban, ufw
   - Configures fail2ban service with custom jail configuration
     - Template: fail2ban.jail.local.erb → /etc/fail2ban/jail.local
   - Sets up UFW firewall rules: deny default, allow SSH/HTTP/HTTPS
   - Deploys kernel security parameters via sysctl
     - Template: sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf
   - Conditionally disables SSH root login if node['security']['ssh']['disable_root'] is true
   - Conditionally disables SSH password authentication if node['security']['ssh']['password_auth'] is false
   - Resources: package (1), service (1), template (2), execute (6), service (1)

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx package
   - Deploys main nginx configuration
     - Template: nginx.conf.erb → /etc/nginx/nginx.conf
   - Deploys security configuration for nginx
     - Template: security.conf.erb → /etc/nginx/conf.d/security.conf
   - Enables and starts nginx service
   - Iterations: Creates document root directories and deploys index.html files for **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3)

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group for certificate management
   - Creates SSL certificate and private key directories
   - Iterations: Generates self-signed SSL certificates for **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Sets proper permissions (640) and ownership (root:ssl-cert) on private keys
     - Certificate details: RSA 2048-bit, 365 days validity, US/Example organization
   - Resources: package (1), group (1), directory (2), execute (3)

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterations: Deploys nginx virtual host configurations for **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Template: site.conf.erb → /etc/nginx/sites-available/{site_name}
     - Creates symbolic link to enable each site: /etc/nginx/sites-available/{site_name} → /etc/nginx/sites-enabled/{site_name}
   - Removes default nginx site configuration
   - Resources: template (3), link (3), file (1)

## Dependencies

**External cookbook dependencies**: None (standalone cookbook)
**System package dependencies**: nginx, fail2ban, ufw, openssl, ca-certificates
**Service dependencies**: nginx, fail2ban, ssh

## Credentials

**Detection Summary**: No credentials detected across all files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. SSL certificates are generated as self-signed certificates with hardcoded organizational information.

## Checks for the Migration

**Files to verify**:
- /etc/nginx/nginx.conf
- /etc/nginx/conf.d/security.conf
- /etc/nginx/sites-available/test.cluster.local
- /etc/nginx/sites-available/ci.cluster.local
- /etc/nginx/sites-available/status.cluster.local
- /etc/nginx/sites-enabled/test.cluster.local
- /etc/nginx/sites-enabled/ci.cluster.local
- /etc/nginx/sites-enabled/status.cluster.local
- /etc/fail2ban/jail.local
- /etc/sysctl.d/99-security.conf
- /opt/server/test/index.html
- /opt/server/ci/index.html
- /opt/server/status/index.html
- /etc/ssl/certs/test.cluster.local.crt
- /etc/ssl/certs/ci.cluster.local.crt
- /etc/ssl/certs/status.cluster.local.crt
- /etc/ssl/private/test.cluster.local.key
- /etc/ssl/private/ci.cluster.local.key
- /etc/ssl/private/status.cluster.local.key

**Service endpoints to check**: 80 (HTTP), 443 (HTTPS), 22 (SSH)
**Templates rendered**:
- fail2ban.jail.local.erb (1 time)
- nginx.conf.erb (1 time)
- security.conf.erb (1 time)
- sysctl-security.conf.erb (1 time)
- site.conf.erb (3 times)

## Pre-flight checks:
```bash
# Service status
systemctl status nginx
systemctl status fail2ban
ps aux | grep nginx
ps aux | grep fail2ban

# Nginx configuration validation
nginx -t
nginx -T | grep -E 'server_name|listen|ssl_certificate'

# Site: test.cluster.local
curl -I http://test.cluster.local
curl -I https://test.cluster.local
curl -s http://test.cluster.local | grep -i "test"
openssl s_client -connect test.cluster.local:443 -servername test.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# Site: ci.cluster.local
curl -I http://ci.cluster.local
curl -I https://ci.cluster.local
curl -s http://ci.cluster.local | grep -i "ci"
openssl s_client -connect ci.cluster.local:443 -servername ci.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# Site: status.cluster.local
curl -I http://status.cluster.local
curl -I https://status.cluster.local
curl -s http://status.cluster.local | grep -i "status"
openssl s_client -connect status.cluster.local:443 -servername status.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# SSL certificate verification
ls -lah /etc/ssl/certs/test.cluster.local.crt
ls -lah /etc/ssl/certs/ci.cluster.local.crt
ls -lah /etc/ssl/certs/status.cluster.local.crt
ls -lah /etc/ssl/private/test.cluster.local.key
ls -lah /etc/ssl/private/ci.cluster.local.key
ls -lah /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -dates

# Document root verification
ls -lah /opt/server/test/index.html
ls -lah /opt/server/ci/index.html
ls -lah /opt/server/status/index.html
cat /opt/server/test/index.html
cat /opt/server/ci/index.html
cat /opt/server/status/index.html

# Security configuration checks
fail2ban-client status
ufw status verbose
cat /etc/fail2ban/jail.local | grep -E 'enabled|bantime|findtime|maxretry'
cat /etc/sysctl.d/99-security.conf
sysctl -a | grep -E 'net.ipv4.tcp_syncookies|net.ipv4.ip_forward|kernel.dmesg_restrict'

# Network listening verification
netstat -tulpn | grep nginx
netstat -tulpn | grep :80
netstat -tulpn | grep :443
ss -tlnp | grep nginx
lsof -i :80
lsof -i :443
```