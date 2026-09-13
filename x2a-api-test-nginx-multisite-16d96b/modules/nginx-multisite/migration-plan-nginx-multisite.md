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
   - Resources: package (1), service (1), template (2), execute (5), service (1)
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
     - Generates self-signed SSL certificate for each site
     - Sets certificate permissions (640) and ownership (root:ssl-cert)
   - Resources: package (1), group (1), directory (2), execute (3)
   - Certificate paths:
     - /etc/ssl/certs/{site_name}.crt
     - /etc/ssl/private/{site_name}.key

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Deploys nginx virtual host configuration for each site
     - Creates symbolic link to enable each site
   - Removes default nginx site configuration
   - Resources: template (3), link (3), file (1)
   - Templates:
     - site.conf.erb → /etc/nginx/sites-available/{site_name} (3 times)

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
- /opt/server/test/index.html (test site content)
- /opt/server/ci/index.html (ci site content)
- /opt/server/status/index.html (status site content)
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
- Network interfaces: Binds to all interfaces (0.0.0.0)

**Templates rendered**:
- fail2ban.jail.local.erb renders 1 time to /etc/fail2ban/jail.local
- nginx.conf.erb renders 1 time to /etc/nginx/nginx.conf
- security.conf.erb renders 1 time to /etc/nginx/conf.d/security.conf
- sysctl-security.conf.erb renders 1 time to /etc/sysctl.d/99-security.conf
- site.conf.erb renders 3 times to /etc/nginx/sites-available/{site_name}

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

# Site-specific checks - MUST test each site individually
# Site: test.cluster.local
curl -I http://test.cluster.local  # should return 301 redirect to HTTPS
curl -I https://test.cluster.local  # should return 200 OK
curl -s https://test.cluster.local | grep "Test Environment"
openssl s_client -connect test.cluster.local:443 -servername test.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject
ls -la /opt/server/test/index.html
cat /etc/nginx/sites-available/test.cluster.local | grep server_name

# Site: ci.cluster.local
curl -I http://ci.cluster.local  # should return 301 redirect to HTTPS
curl -I https://ci.cluster.local  # should return 200 OK
curl -s https://ci.cluster.local | grep "CI Environment"
openssl s_client -connect ci.cluster.local:443 -servername ci.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject
ls -la /opt/server/ci/index.html
cat /etc/nginx/sites-available/ci.cluster.local | grep server_name

# Site: status.cluster.local
curl -I http://status.cluster.local  # should return 301 redirect to HTTPS
curl -I https://status.cluster.local  # should return 200 OK
curl -s https://status.cluster.local | grep "Status Environment"
openssl s_client -connect status.cluster.local:443 -servername status.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject
ls -la /opt/server/status/index.html
cat /etc/nginx/sites-available/status.cluster.local | grep server_name

# SSL certificate validation - check each certificate individually
# Certificate: test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN='
ls -la /etc/ssl/private/test.cluster.local.key  # should show 640 permissions, root:ssl-cert ownership

# Certificate: ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN='
ls -la /etc/ssl/private/ci.cluster.local.key  # should show 640 permissions, root:ssl-cert ownership

# Certificate: status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN='
ls -la /etc/ssl/private/status.cluster.local.key  # should show 640 permissions, root:ssl-cert ownership

# Security configuration validation
cat /etc/fail2ban/jail.local | grep -E 'enabled|bantime|findtime|maxretry'
fail2ban-client status
fail2ban-client status sshd

# UFW firewall status
ufw status verbose  # should show: deny (incoming), allow (outgoing), allow 22/tcp, allow 80/tcp, allow 443/tcp
iptables -L -n | grep -E '22|80|443'

# SSH security validation
cat /etc/ssh/sshd_config | grep -E 'PermitRootLogin|PasswordAuthentication'  # should show 'no' for both
sshd -T | grep -E 'permitrootlogin|passwordauthentication'

# Kernel security parameters
sysctl -a | grep -f /etc/sysctl.d/99-security.conf
cat /etc/sysctl.d/99-security.conf

# Logs - check each service
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/test.cluster.local_access.log
tail -f /var/log/nginx/ci.cluster.local_access.log
tail -f /var/log/nginx/status.cluster.local_access.log
tail -f /var/log/fail2ban.log
journalctl -u nginx -f
journalctl -u fail2ban -f

# Network listening
netstat -tulpn | grep -E ':80|:443|:22'
ss -tlnp | grep nginx
lsof -i :80
lsof -i :443

# Directory permissions and ownership
ls -la /opt/server/
ls -la /opt/server/test/
ls -la /opt/server/ci/
ls -la /opt/server/status/
ls -la /etc/ssl/certs/ | grep cluster.local
ls -la /etc/ssl/private/ | grep cluster.local
getent group ssl-cert

# Security headers validation - test each site
curl -I https://test.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'
curl -I https://ci.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'
curl -I https://status.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'
```