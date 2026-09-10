---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Web server cookbook that configures Nginx with 3 virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), implements comprehensive security hardening with fail2ban/UFW, generates self-signed SSL certificates for each site, and deploys static HTML content.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:
- **test.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/test
  - Port/Socket: 80 (HTTP), 443 (HTTPS)
  - Key Config: SSL certificate at /etc/ssl/certs/test.cluster.local.crt

- **ci.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/ci
  - Port/Socket: 80 (HTTP), 443 (HTTPS)
  - Key Config: SSL certificate at /etc/ssl/certs/ci.cluster.local.crt

- **status.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/status
  - Port/Socket: 80 (HTTP), 443 (HTTPS)
  - Key Config: SSL certificate at /etc/ssl/certs/status.cluster.local.crt

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

1. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs security packages: fail2ban, ufw
   - Configures fail2ban service with custom jail configuration
     - Template: fail2ban.jail.local.erb → /etc/fail2ban/jail.local
   - Sets up UFW firewall rules: deny default, allow SSH/HTTP/HTTPS
   - Deploys kernel security parameters via sysctl
     - Template: sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf
   - Conditionally disables SSH root login if node['security']['ssh']['disable_root'] is true
   - Conditionally disables SSH password authentication if node['security']['ssh']['password_auth'] is false
   - Resources: package (1), service (1), template (2), execute (6)

2. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx package
   - Deploys main nginx configuration
     - Template: nginx.conf.erb → /etc/nginx/nginx.conf
   - Deploys security configuration for nginx
     - Template: security.conf.erb → /etc/nginx/conf.d/security.conf
   - Enables and starts nginx service
   - Iterations: Creates document root and deploys content for **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Creates document root directory for each site
     - Deploys static index.html file to each document root
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3)

3. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group for certificate management
   - Creates SSL certificate and private key directories: /etc/ssl/certs, /etc/ssl/private
   - Iterations: Generates SSL certificates for **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Generates self-signed SSL certificate for each site (365 days validity)
     - Sets certificate permissions (640) and ownership (root:ssl-cert)
   - Resources: package (1), group (1), directory (2), execute (3)

4. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterations: Configures virtual hosts for **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Deploys nginx virtual host configuration for each site
       - Template: site.conf.erb → /etc/nginx/sites-available/{site_name}
     - Creates symbolic link to enable each site
       - Link: /etc/nginx/sites-available/{site_name} → /etc/nginx/sites-enabled/{site_name}
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

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. SSL certificates are generated as self-signed certificates without external credential requirements.

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
- /opt/server/test/index.html
- /opt/server/ci/index.html
- /opt/server/status/index.html
- /etc/ssl/certs/test.cluster.local.crt
- /etc/ssl/certs/ci.cluster.local.crt
- /etc/ssl/certs/status.cluster.local.crt
- /etc/ssl/private/test.cluster.local.key
- /etc/ssl/private/ci.cluster.local.key
- /etc/ssl/private/status.cluster.local.key
- /etc/fail2ban/jail.local
- /etc/sysctl.d/99-security.conf

**Service endpoints to check**:
- Ports listening: 80 (HTTP), 443 (HTTPS), 22 (SSH)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
- fail2ban.jail.local.erb → /etc/fail2ban/jail.local (1 time)
- nginx.conf.erb → /etc/nginx/nginx.conf (1 time)
- security.conf.erb → /etc/nginx/conf.d/security.conf (1 time)
- sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf (1 time)
- site.conf.erb → /etc/nginx/sites-available/{site_name} (3 times: test.cluster.local, ci.cluster.local, status.cluster.local)

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

# Virtual host checks - test.cluster.local
curl -I http://test.cluster.local/
curl -I -k https://test.cluster.local/
curl -s http://test.cluster.local/ | grep -i "test"
openssl s_client -connect test.cluster.local:443 -servername test.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# Virtual host checks - ci.cluster.local
curl -I http://ci.cluster.local/
curl -I -k https://ci.cluster.local/
curl -s http://ci.cluster.local/ | grep -i "ci"
openssl s_client -connect ci.cluster.local:443 -servername ci.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# Virtual host checks - status.cluster.local
curl -I http://status.cluster.local/
curl -I -k https://status.cluster.local/
curl -s http://status.cluster.local/ | grep -i "status"
openssl s_client -connect status.cluster.local:443 -servername status.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# SSL certificate validation
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:'
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:'
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:'

# SSL private key validation
openssl rsa -in /etc/ssl/private/test.cluster.local.key -check -noout
openssl rsa -in /etc/ssl/private/ci.cluster.local.key -check -noout
openssl rsa -in /etc/ssl/private/status.cluster.local.key -check -noout

# Security configuration validation
fail2ban-client status
fail2ban-client status nginx-http-auth
fail2ban-client status ssh
ufw status verbose
grep -E 'PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config
sysctl -a | grep -f /etc/sysctl.d/99-security.conf

# Network listening verification
netstat -tulpn | grep -E ':80|:443|:22'
ss -tlnp | grep nginx | grep -E ':80|:443'
lsof -i :80
lsof -i :443
```