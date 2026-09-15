---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Web server cookbook that configures Nginx with 3 SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), implements comprehensive security hardening with fail2ban, UFW firewall, SSH restrictions, and kernel security parameters. Each site serves static content from dedicated document roots with self-signed SSL certificates.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:
- **test.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/test (document root)
  - Port/Socket: 80 (HTTP), 443 (HTTPS)
  - Key Config: SSL certificate at /etc/ssl/certs/test.cluster.local.crt, private key at /etc/ssl/private/test.cluster.local.key

- **ci.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/ci (document root)
  - Port/Socket: 80 (HTTP), 443 (HTTPS)
  - Key Config: SSL certificate at /etc/ssl/certs/ci.cluster.local.crt, private key at /etc/ssl/private/ci.cluster.local.key

- **status.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/status (document root)
  - Port/Socket: 80 (HTTP), 443 (HTTPS)
  - Key Config: SSL certificate at /etc/ssl/certs/status.cluster.local.crt, private key at /etc/ssl/private/status.cluster.local.key

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
   - Resources: package (1), service (1), template (2), execute (7), service (1)

2. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx package
   - Deploys main nginx configuration
     - Template: nginx.conf.erb → /etc/nginx/nginx.conf
   - Deploys security configuration for nginx
     - Template: security.conf.erb → /etc/nginx/conf.d/security.conf
   - Enables and starts nginx service
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Creates document root directory for each site (/opt/server/test, /opt/server/ci, /opt/server/status)
     - Deploys static index.html file to each document root
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3)

3. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group for certificate management
   - Creates SSL certificate and private key directories (/etc/ssl/certs, /etc/ssl/private)
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Generates self-signed SSL certificate for each site using OpenSSL
     - Sets certificate subject: /C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN={site_name}/emailAddress=admin@example.com
     - Sets proper permissions (640) and ownership (root:ssl-cert) on private keys
   - Resources: package (1), group (1), directory (2), execute (3)

4. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Deploys nginx virtual host configuration for each site
       - Template: site.conf.erb → /etc/nginx/sites-available/{site_name}
     - Creates symbolic link to enable each site
       - Link: /etc/nginx/sites-available/{site_name} → /etc/nginx/sites-enabled/{site_name}
   - Removes default nginx site configuration
   - Resources: template (3), link (3), file (1)

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

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. SSL certificates are self-signed and generated locally without external credential requirements.

## Checks for the Migration

**Files to verify**:
- /etc/nginx/nginx.conf (main nginx configuration)
- /etc/nginx/conf.d/security.conf (nginx security settings)
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

# Virtual host checks - verify each site individually
# Site: test.cluster.local
curl -I http://test.cluster.local/
curl -I -k https://test.cluster.local/
curl -s http://test.cluster.local/ | grep -i "test"
openssl s_client -connect test.cluster.local:443 -servername test.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# Site: ci.cluster.local
curl -I http://ci.cluster.local/
curl -I -k https://ci.cluster.local/
curl -s http://ci.cluster.local/ | grep -i "ci"
openssl s_client -connect ci.cluster.local:443 -servername ci.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# Site: status.cluster.local
curl -I http://status.cluster.local/
curl -I -k https://status.cluster.local/
curl -s http://status.cluster.local/ | grep -i "status"
openssl s_client -connect status.cluster.local:443 -servername status.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# SSL certificate validation - check each certificate
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:'
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:'
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:'

# Private key validation - check permissions and ownership
ls -l /etc/ssl/private/test.cluster.local.key | grep "root ssl-cert"
ls -l /etc/ssl/private/ci.cluster.local.key | grep "root ssl-cert"
ls -l /etc/ssl/private/status.cluster.local.key | grep "root ssl-cert"
stat -c "%a" /etc/ssl/private/test.cluster.local.key  # should show 640
stat -c "%a" /etc/ssl/private/ci.cluster.local.key   # should show 640
stat -c "%a" /etc/ssl/private/status.cluster.local.key # should show 640

# Document root validation
ls -lah /opt/server/test/index.html
ls -lah /opt/server/ci/index.html
ls -lah /opt/server/status/index.html
cat /opt/server/test/index.html
cat /opt/server/ci/index.html
cat /opt/server/status/index.html

# Security configuration validation
fail2ban-client status
fail2ban-client status nginx-http-auth
ufw status verbose
cat /etc/fail2ban/jail.local | grep -E 'enabled|bantime|findtime|maxretry'
cat /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects

# SSH security validation
grep "PermitRootLogin" /etc/ssh/sshd_config  # should show "no"
grep "PasswordAuthentication" /etc/ssh/sshd_config  # should show "no"
sshd -T | grep -E 'permitrootlogin|passwordauthentication'

# Network listening validation
netstat -tulpn | grep :80
netstat -tulpn | grep :443
netstat -tulpn | grep :22
ss -tlnp | grep nginx
lsof -i :80
lsof -i :443

# Nginx site configuration validation
ls -l /etc/nginx/sites-enabled/ | grep -E 'test.cluster.local|ci.cluster.local|status.cluster.local'
ls -l /etc/nginx/sites-enabled/default  # should not exist
cat /etc/nginx/sites-available/test.cluster.local | grep -E 'server_name|document_root|ssl_certificate'
cat /etc/nginx/sites-available/ci.cluster.local | grep -E 'server_name|document_root|ssl_certificate'
cat /etc/nginx/sites-available/status.cluster.local | grep -E 'server_name|document_root|ssl_certificate'

# Logs validation
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
tail -f /var/log/fail2ban.log
journalctl -u nginx -f
journalctl -u fail2ban -f

# Firewall rules validation
iptables -L -n | grep -E '22|80|443'
ufw status numbered
```