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

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Orchestrates the complete setup by including all other recipes
   - Resources: include_recipe (4)

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs security packages: fail2ban, ufw
   - Configures fail2ban with custom jail settings
     - Template: fail2ban.jail.local.erb → /etc/fail2ban/jail.local
   - Sets up UFW firewall rules: deny default, allow SSH/HTTP/HTTPS
   - Deploys kernel security parameters
     - Template: sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf
   - Hardens SSH configuration (conditionally):
     - Disables root login if node['security']['ssh']['disable_root'] = true
     - Disables password authentication if node['security']['ssh']['password_auth'] = false
   - Resources: package (1), service (1), template (2), execute (6), service (1)

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx package
   - Deploys main nginx configuration
     - Template: nginx.conf.erb → /etc/nginx/nginx.conf
   - Deploys security configuration
     - Template: security.conf.erb → /etc/nginx/conf.d/security.conf
   - Enables and starts nginx service
   - Creates document root directory for **test.cluster.local**
   - Deploys static index.html file to /opt/server/test
   - Creates document root directory for **ci.cluster.local**
   - Deploys static index.html file to /opt/server/ci
   - Creates document root directory for **status.cluster.local**
   - Deploys static index.html file to /opt/server/status
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3)

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group for certificate management
   - Creates SSL certificate and private key directories:
     - /etc/ssl/certs (mode 0755)
     - /etc/ssl/private (mode 0710, group ssl-cert)
   - Generates self-signed SSL certificate for **test.cluster.local** (365 days validity)
     - Certificate: /etc/ssl/certs/test.cluster.local.crt
     - Private key: /etc/ssl/private/test.cluster.local.key (mode 640, owner root:ssl-cert)
   - Generates self-signed SSL certificate for **ci.cluster.local** (365 days validity)
     - Certificate: /etc/ssl/certs/ci.cluster.local.crt
     - Private key: /etc/ssl/private/ci.cluster.local.key (mode 640, owner root:ssl-cert)
   - Generates self-signed SSL certificate for **status.cluster.local** (365 days validity)
     - Certificate: /etc/ssl/certs/status.cluster.local.crt
     - Private key: /etc/ssl/private/status.cluster.local.key (mode 640, owner root:ssl-cert)
   - Resources: package (1), group (1), directory (2), execute (3)

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Deploys nginx virtual host configuration for **test.cluster.local**
     - Template: site.conf.erb → /etc/nginx/sites-available/test.cluster.local
   - Creates symbolic link to enable **test.cluster.local** site
     - Link: /etc/nginx/sites-available/test.cluster.local → /etc/nginx/sites-enabled/test.cluster.local
   - Deploys nginx virtual host configuration for **ci.cluster.local**
     - Template: site.conf.erb → /etc/nginx/sites-available/ci.cluster.local
   - Creates symbolic link to enable **ci.cluster.local** site
     - Link: /etc/nginx/sites-available/ci.cluster.local → /etc/nginx/sites-enabled/ci.cluster.local
   - Deploys nginx virtual host configuration for **status.cluster.local**
     - Template: site.conf.erb → /etc/nginx/sites-available/status.cluster.local
   - Creates symbolic link to enable **status.cluster.local** site
     - Link: /etc/nginx/sites-available/status.cluster.local → /etc/nginx/sites-enabled/status.cluster.local
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

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. SSL certificates are self-signed and generated locally without external credential requirements.

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
- Unix sockets: None
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

# SSL certificate verification - test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN='
ls -la /etc/ssl/private/test.cluster.local.key
stat -c "%a %U:%G" /etc/ssl/private/test.cluster.local.key

# SSL certificate verification - ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN='
ls -la /etc/ssl/private/ci.cluster.local.key
stat -c "%a %U:%G" /etc/ssl/private/ci.cluster.local.key

# SSL certificate verification - status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN='
ls -la /etc/ssl/private/status.cluster.local.key
stat -c "%a %U:%G" /etc/ssl/private/status.cluster.local.key

# Document root verification
ls -la /opt/server/test/index.html
ls -la /opt/server/ci/index.html
ls -la /opt/server/status/index.html
cat /opt/server/test/index.html | head -5
cat /opt/server/ci/index.html | head -5
cat /opt/server/status/index.html | head -5

# Security configuration validation
fail2ban-client status
fail2ban-client status nginx-http-auth
ufw status verbose
cat /etc/fail2ban/jail.local | grep -E 'enabled|bantime|maxretry'
cat /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects

# SSH hardening verification
grep -E 'PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config
sshd -T | grep -E 'permitrootlogin|passwordauthentication'

# Network listening verification
netstat -tulpn | grep :80
netstat -tulpn | grep :443
netstat -tulpn | grep :22
ss -tlnp | grep nginx
lsof -i :80
lsof -i :443

# Nginx site configuration verification
ls -la /etc/nginx/sites-available/
ls -la /etc/nginx/sites-enabled/
ls -la /etc/nginx/sites-enabled/default
nginx -T | grep server_name | sort

# Logs verification
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
tail -f /var/log/fail2ban.log
journalctl -u nginx -f
journalctl -u fail2ban -f

# Firewall rules verification
iptables -L -n | grep -E '80|443|22'
ufw status numbered
```