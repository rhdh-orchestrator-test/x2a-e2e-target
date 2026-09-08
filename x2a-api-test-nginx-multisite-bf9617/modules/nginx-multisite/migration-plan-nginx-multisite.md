---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Multi-site nginx web server cookbook that configures 3 SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) with comprehensive security hardening including fail2ban, UFW firewall, SSH hardening, and kernel security parameters.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Testing and development environment
  - Location/Path: /opt/server/test
  - Port/Socket: HTTP 80 (redirects to HTTPS), HTTPS 443
  - Key Config: SSL enabled, self-signed certificate, security headers, gzip compression

- **ci.cluster.local**: Continuous integration environment  
  - Location/Path: /opt/server/ci
  - Port/Socket: HTTP 80 (redirects to HTTPS), HTTPS 443
  - Key Config: SSL enabled, self-signed certificate, security headers, gzip compression

- **status.cluster.local**: Status monitoring environment
  - Location/Path: /opt/server/status
  - Port/Socket: HTTP 80 (redirects to HTTPS), HTTPS 443
  - Key Config: SSL enabled, self-signed certificate, security headers, gzip compression

## File Structure

**Recipes:**
```
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
```

**Templates:**
```
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
```

**Attributes:**
```
cookbooks/nginx-multisite/attributes/default.rb
```

**Files:**
```
cookbooks/nginx-multisite/files/default/test/index.html
cookbooks/nginx-multisite/files/default/ci/index.html
cookbooks/nginx-multisite/files/default/status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Orchestrates the complete setup by including all other recipes
   - Resources: include_recipe (4)

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs security packages: fail2ban, ufw
   - Configures fail2ban service with custom jail configuration
   - Sets up UFW firewall rules: deny default, allow SSH/HTTP/HTTPS
   - Deploys kernel security parameters via sysctl
   - Conditionally disables SSH root login if node['security']['ssh']['disable_root'] is true
   - Conditionally disables SSH password authentication if node['security']['ssh']['password_auth'] is false
   - Resources: package (1), service (1), template (2), execute (6), service (1)
   - Templates:
     - fail2ban.jail.local.erb → /etc/fail2ban/jail.local
     - sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx package
   - Deploys main nginx configuration and security configuration
   - Enables and starts nginx service
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Creates document root directory for each site
     - Deploys static index.html file for each site from files/default/{site}/index.html
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3)
   - Templates:
     - nginx.conf.erb → /etc/nginx/nginx.conf
     - security.conf.erb → /etc/nginx/conf.d/security.conf

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group and SSL directories
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Generates self-signed SSL certificate for each site (RSA 2048-bit, 365 days validity)
     - Sets certificate permissions (640) and ownership (root:ssl-cert)
   - Resources: package (1), group (1), directory (2), execute (3)
   - Certificate paths:
     - Certificates: /etc/ssl/certs/{site_name}.crt
     - Private keys: /etc/ssl/private/{site_name}.key

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Deploys nginx virtual host configuration for each site
     - Creates symbolic link to enable each site
     - Configures HTTP to HTTPS redirect, SSL settings, security headers, gzip compression
   - Removes default nginx site configuration
   - Resources: template (3), link (3), file (1)
   - Templates:
     - site.conf.erb → /etc/nginx/sites-available/{site_name} (3 times)

## Dependencies

**External cookbook dependencies**: None (standalone cookbook)
**System package dependencies**: nginx, fail2ban, ufw, openssl, ca-certificates
**Service dependencies**: nginx, fail2ban, ssh, ufw

## Credentials

**Detection Summary**: No credentials detected across all files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. SSL certificates are generated as self-signed certificates with hardcoded subject information for development/testing purposes.

## Checks for the Migration

**Files to verify**:
- /etc/nginx/nginx.conf (main nginx configuration)
- /etc/nginx/conf.d/security.conf (security headers configuration)
- /etc/nginx/sites-available/test.cluster.local (virtual host config)
- /etc/nginx/sites-available/ci.cluster.local (virtual host config)
- /etc/nginx/sites-available/status.cluster.local (virtual host config)
- /etc/nginx/sites-enabled/test.cluster.local (enabled site symlink)
- /etc/nginx/sites-enabled/ci.cluster.local (enabled site symlink)
- /etc/nginx/sites-enabled/status.cluster.local (enabled site symlink)
- /opt/server/test/index.html (static content)
- /opt/server/ci/index.html (static content)
- /opt/server/status/index.html (static content)
- /etc/ssl/certs/test.cluster.local.crt (SSL certificate)
- /etc/ssl/certs/ci.cluster.local.crt (SSL certificate)
- /etc/ssl/certs/status.cluster.local.crt (SSL certificate)
- /etc/ssl/private/test.cluster.local.key (SSL private key)
- /etc/ssl/private/ci.cluster.local.key (SSL private key)
- /etc/ssl/private/status.cluster.local.key (SSL private key)
- /etc/fail2ban/jail.local (fail2ban configuration)
- /etc/sysctl.d/99-security.conf (kernel security parameters)

**Service endpoints to check**:
- Ports listening: 80 (HTTP), 443 (HTTPS), 22 (SSH)
- Unix sockets: None
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
- fail2ban.jail.local.erb → /etc/fail2ban/jail.local (1 time)
- nginx.conf.erb → /etc/nginx/nginx.conf (1 time)
- security.conf.erb → /etc/nginx/conf.d/security.conf (1 time)
- sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf (1 time)
- site.conf.erb → /etc/nginx/sites-available/{site_name} (3 times)

## Pre-flight checks:

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
ps aux | grep nginx
ps aux | grep fail2ban

# Web server connectivity - test.cluster.local
curl -I http://test.cluster.local
curl -I https://test.cluster.local
curl -s https://test.cluster.local | grep "Test Environment"
openssl s_client -connect test.cluster.local:443 -servername test.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# Web server connectivity - ci.cluster.local
curl -I http://ci.cluster.local
curl -I https://ci.cluster.local
curl -s https://ci.cluster.local | grep -i "ci\|continuous"
openssl s_client -connect ci.cluster.local:443 -servername ci.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# Web server connectivity - status.cluster.local
curl -I http://status.cluster.local
curl -I https://status.cluster.local
curl -s https://status.cluster.local | grep -i "status\|monitoring"
openssl s_client -connect status.cluster.local:443 -servername status.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# SSL certificate validation
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|Signature Algorithm'
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|Signature Algorithm'
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|Signature Algorithm'

# SSL private key validation
openssl rsa -in /etc/ssl/private/test.cluster.local.key -check -noout
openssl rsa -in /etc/ssl/private/ci.cluster.local.key -check -noout
openssl rsa -in /etc/ssl/private/status.cluster.local.key -check -noout

# Configuration validation
nginx -t
cat /etc/nginx/nginx.conf | grep -E 'worker_processes|worker_connections'
cat /etc/nginx/conf.d/security.conf | grep -E 'server_tokens|add_header'

# Virtual host configuration validation
cat /etc/nginx/sites-available/test.cluster.local | grep -E 'server_name|root|ssl_certificate'
cat /etc/nginx/sites-available/ci.cluster.local | grep -E 'server_name|root|ssl_certificate'
cat /etc/nginx/sites-available/status.cluster.local | grep -E 'server_name|root|ssl_certificate'

# Site enablement verification
ls -la /etc/nginx/sites-enabled/ | grep -E 'test.cluster.local|ci.cluster.local|status.cluster.local'
ls -la /etc/nginx/sites-enabled/default

# Security configuration validation
fail2ban-client status
ufw status
cat /etc/fail2ban/jail.local | grep -E 'enabled|bantime|maxretry'
cat /etc/sysctl.d/99-security.conf | grep -E 'net.ipv4|kernel'

# Document root and content verification
ls -la /opt/server/test/index.html
ls -la /opt/server/ci/index.html  
ls -la /opt/server/status/index.html
cat /opt/server/test/index.html | grep "test.cluster.local"
cat /opt/server/ci/index.html | grep "ci.cluster.local"
cat /opt/server/status/index.html | grep "status.cluster.local"

# Network listening verification
netstat -tulpn | grep :80
netstat -tulpn | grep :443
netstat -tulpn | grep :22
ss -tlnp | grep nginx
lsof -i :80
lsof -i :443

# Security headers verification
curl -I https://test.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'
curl -I https://ci.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'
curl -I https://status.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'

# File permissions verification
ls -la /etc/ssl/private/ | grep -E 'test.cluster.local.key|ci.cluster.local.key|status.cluster.local.key'
ls -la /etc/ssl/certs/ | grep -E 'test.cluster.local.crt|ci.cluster.local.crt|status.cluster.local.crt'
```