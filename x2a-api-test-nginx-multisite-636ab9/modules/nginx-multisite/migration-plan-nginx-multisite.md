---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Multi-site nginx web server cookbook that configures 3 SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) with comprehensive security hardening including fail2ban, UFW firewall, SSH hardening, and security headers. Each site serves static content from separate document roots with self-signed SSL certificates.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:
- **test.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/test
  - Port/Socket: 80 (redirects to 443), 443 (HTTPS)
  - Key Config: SSL certificate at /etc/ssl/certs/test.cluster.local.crt, serves static HTML

- **ci.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/ci
  - Port/Socket: 80 (redirects to 443), 443 (HTTPS)
  - Key Config: SSL certificate at /etc/ssl/certs/ci.cluster.local.crt, serves static HTML

- **status.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/status
  - Port/Socket: 80 (redirects to 443), 443 (HTTPS)
  - Key Config: SSL certificate at /etc/ssl/certs/status.cluster.local.crt, serves static HTML

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
   - Conditionally disables SSH root login (if node['security']['ssh']['disable_root'] = true)
   - Conditionally disables SSH password authentication (if node['security']['ssh']['password_auth'] = false)
   - Resources: package (1), service (1), template (2), execute (5), service (1)
   - Templates:
     - fail2ban.jail.local.erb → /etc/fail2ban/jail.local
     - sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx package
   - Deploys main nginx configuration and security configuration
   - Enables and starts nginx service
   - Creates document root directory for **test.cluster.local** (/opt/server/test)
   - Creates document root directory for **ci.cluster.local** (/opt/server/ci)
   - Creates document root directory for **status.cluster.local** (/opt/server/status)
   - Deploys static index.html file for **test.cluster.local** from cookbook files
   - Deploys static index.html file for **ci.cluster.local** from cookbook files
   - Deploys static index.html file for **status.cluster.local** from cookbook files
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3)
   - Templates:
     - nginx.conf.erb → /etc/nginx/nginx.conf
     - security.conf.erb → /etc/nginx/conf.d/security.conf

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group and SSL directories
   - Generates self-signed SSL certificate for **test.cluster.local**
   - Generates self-signed SSL certificate for **ci.cluster.local**
   - Generates self-signed SSL certificate for **status.cluster.local**
   - Certificate: /etc/ssl/certs/{site_name}.crt
   - Private key: /etc/ssl/private/{site_name}.key (640 permissions, root:ssl-cert ownership)
   - Resources: package (1), group (1), directory (2), execute (3)

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Deploys nginx virtual host configuration for **test.cluster.local**
   - Deploys nginx virtual host configuration for **ci.cluster.local**
   - Deploys nginx virtual host configuration for **status.cluster.local**
   - Creates symlink to enable **test.cluster.local** site
   - Creates symlink to enable **ci.cluster.local** site
   - Creates symlink to enable **status.cluster.local** site
   - Each site configured with SSL redirect (HTTP → HTTPS), security headers, gzip compression
   - Removes default nginx site configuration
   - Resources: template (3), link (3), file (1)
   - Templates:
     - site.conf.erb → /etc/nginx/sites-available/test.cluster.local
     - site.conf.erb → /etc/nginx/sites-available/ci.cluster.local
     - site.conf.erb → /etc/nginx/sites-available/status.cluster.local

## Dependencies

**External cookbook dependencies**: None (standalone cookbook)
**System package dependencies**: nginx, fail2ban, ufw, openssl, ca-certificates
**Service dependencies**: nginx, fail2ban, ssh

## Credentials

**Detection Summary**: No credentials detected across 5 files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. SSL certificates are self-signed and generated locally without external credential requirements.

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
- Network interfaces: Binds to all interfaces (0.0.0.0)

**Templates rendered**:
- fail2ban.jail.local.erb renders 1 time to /etc/fail2ban/jail.local
- nginx.conf.erb renders 1 time to /etc/nginx/nginx.conf
- security.conf.erb renders 1 time to /etc/nginx/conf.d/security.conf
- sysctl-security.conf.erb renders 1 time to /etc/sysctl.d/99-security.conf
- site.conf.erb renders 3 times (once per site) to /etc/nginx/sites-available/{site_name}

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
curl -I http://test.cluster.local  # should return 301 redirect to HTTPS
curl -I -k https://test.cluster.local  # should return 200 OK
curl -s -k https://test.cluster.local | grep -i "test"
openssl s_client -connect test.cluster.local:443 -servername test.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# Virtual host checks - ci.cluster.local
curl -I http://ci.cluster.local  # should return 301 redirect to HTTPS
curl -I -k https://ci.cluster.local  # should return 200 OK
curl -s -k https://ci.cluster.local | grep -i "ci"
openssl s_client -connect ci.cluster.local:443 -servername ci.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# Virtual host checks - status.cluster.local
curl -I http://status.cluster.local  # should return 301 redirect to HTTPS
curl -I -k https://status.cluster.local  # should return 200 OK
curl -s -k https://status.cluster.local | grep -i "status"
openssl s_client -connect status.cluster.local:443 -servername status.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# SSL certificate validation - test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | grep -E 'Subject:|Issuer:|Not After'
ls -la /etc/ssl/private/test.cluster.local.key  # should show 640 root:ssl-cert

# SSL certificate validation - ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | grep -E 'Subject:|Issuer:|Not After'
ls -la /etc/ssl/private/ci.cluster.local.key  # should show 640 root:ssl-cert

# SSL certificate validation - status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | grep -E 'Subject:|Issuer:|Not After'
ls -la /etc/ssl/private/status.cluster.local.key  # should show 640 root:ssl-cert

# Security configuration validation
cat /etc/nginx/conf.d/security.conf | grep -E 'X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'
curl -I -k https://test.cluster.local | grep -E 'X-Frame-Options|Strict-Transport-Security|X-Content-Type-Options'

# Firewall status
ufw status verbose  # should show allow 22/tcp, 80/tcp, 443/tcp and default deny incoming
iptables -L -n | grep -E 'DROP|ACCEPT'

# Fail2ban status
fail2ban-client status
fail2ban-client status sshd  # should show jail is active
cat /etc/fail2ban/jail.local | grep -E 'enabled|bantime|maxretry'

# SSH security validation
grep -E 'PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config
sshd -T | grep -E 'permitrootlogin|passwordauthentication'

# Kernel security parameters
sysctl -a | grep -f /etc/sysctl.d/99-security.conf
cat /etc/sysctl.d/99-security.conf

# Document root and content verification - test.cluster.local
ls -la /opt/server/test/index.html  # should show www-data:www-data ownership
cat /opt/server/test/index.html

# Document root and content verification - ci.cluster.local
ls -la /opt/server/ci/index.html    # should show www-data:www-data ownership
cat /opt/server/ci/index.html

# Document root and content verification - status.cluster.local
ls -la /opt/server/status/index.html # should show www-data:www-data ownership
cat /opt/server/status/index.html

# Logs - test.cluster.local
tail -f /var/log/nginx/test.cluster.local_access.log
tail -f /var/log/nginx/test.cluster.local_error.log

# Logs - ci.cluster.local
tail -f /var/log/nginx/ci.cluster.local_access.log
tail -f /var/log/nginx/ci.cluster.local_error.log

# Logs - status.cluster.local
tail -f /var/log/nginx/status.cluster.local_access.log
tail -f /var/log/nginx/status.cluster.local_error.log

# General logs
tail -f /var/log/nginx/error.log
tail -f /var/log/fail2ban.log
journalctl -u nginx -f
journalctl -u fail2ban -f

# Network listening
netstat -tulpn | grep nginx  # should show :80 and :443
ss -tlnp | grep nginx
lsof -i :80
lsof -i :443
lsof -i :22

# Site availability verification
ls -la /etc/nginx/sites-enabled/  # should NOT contain 'default'
ls -la /etc/nginx/sites-enabled/test.cluster.local  # should be symlink to sites-available
ls -la /etc/nginx/sites-enabled/ci.cluster.local    # should be symlink to sites-available
ls -la /etc/nginx/sites-enabled/status.cluster.local # should be symlink to sites-available

# Process and resource checks
ps aux | grep nginx | wc -l  # should show master + worker processes
nginx -V 2>&1 | grep -E 'configure arguments|built'
```