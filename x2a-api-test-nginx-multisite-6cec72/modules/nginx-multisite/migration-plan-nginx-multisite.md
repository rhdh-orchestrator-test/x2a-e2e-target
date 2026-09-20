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
   - Conditionally disables SSH root login if node['security']['ssh']['disable_root'] is true
   - Conditionally disables SSH password authentication if node['security']['ssh']['password_auth'] is false
   - Resources: package (1), service (2), template (2), execute (6)

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx package
   - Deploys main nginx configuration
     - Template: nginx.conf.erb → /etc/nginx/nginx.conf
   - Deploys security configuration
     - Template: security.conf.erb → /etc/nginx/conf.d/security.conf
   - Enables and starts nginx service
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Creates document root directory for each site
     - Deploys index.html file to each document root
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3)

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group for certificate management
   - Creates SSL certificate and private key directories
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Generates self-signed SSL certificate for each site (365 days validity)
     - Sets proper permissions (640) and ownership (root:ssl-cert) on private keys
   - Resources: package (1), group (1), directory (2), execute (3)

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
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
**Service dependencies**: nginx, fail2ban, ssh

## Credentials

**Detection Summary**: No credentials detected across all files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. SSL certificates are self-signed and generated locally.

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
- site.conf.erb → /etc/nginx/sites-available/{site_name} (3 times)

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

# Virtual host checks - test each site individually
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

# SSL certificate verification - check each certificate individually
# Certificate: test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN='
ls -la /etc/ssl/private/test.cluster.local.key
stat -c "%a %U:%G" /etc/ssl/private/test.cluster.local.key  # should show 640 root:ssl-cert

# Certificate: ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN='
ls -la /etc/ssl/private/ci.cluster.local.key
stat -c "%a %U:%G" /etc/ssl/private/ci.cluster.local.key  # should show 640 root:ssl-cert

# Certificate: status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN='
ls -la /etc/ssl/private/status.cluster.local.key
stat -c "%a %U:%G" /etc/ssl/private/status.cluster.local.key  # should show 640 root:ssl-cert

# Document root verification - check each site directory
# Site: test.cluster.local (/opt/server/test)
ls -la /opt/server/test/
cat /opt/server/test/index.html
stat -c "%a %U:%G" /opt/server/test/  # verify permissions

# Site: ci.cluster.local (/opt/server/ci)
ls -la /opt/server/ci/
cat /opt/server/ci/index.html
stat -c "%a %U:%G" /opt/server/ci/  # verify permissions

# Site: status.cluster.local (/opt/server/status)
ls -la /opt/server/status/
cat /opt/server/status/index.html
stat -c "%a %U:%G" /opt/server/status/  # verify permissions

# Security configuration validation
# Fail2ban status
fail2ban-client status
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
cat /etc/fail2ban/jail.local

# UFW firewall status
ufw status verbose
ufw status numbered
iptables -L -n | grep -E '22|80|443'

# SSH security settings
grep -E 'PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config
sshd -T | grep -E 'permitrootlogin|passwordauthentication'

# Kernel security parameters
cat /etc/sysctl.d/99-security.conf
sysctl -a | grep -E 'net.ipv4.ip_forward|net.ipv4.conf.all.send_redirects|kernel.dmesg_restrict'

# Network listening verification
netstat -tulpn | grep -E ':80|:443|:22'
ss -tlnp | grep nginx
lsof -i :80
lsof -i :443

# Nginx site configuration verification
ls -la /etc/nginx/sites-available/
ls -la /etc/nginx/sites-enabled/
test ! -f /etc/nginx/sites-enabled/default && echo "Default site removed" || echo "ERROR: Default site still exists"

# Logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
tail -f /var/log/fail2ban.log
journalctl -u nginx -f
journalctl -u fail2ban -f

# SSL/TLS verification with external tools
for site in test.cluster.local ci.cluster.local status.cluster.local; do
    echo "Testing $site:"
    openssl s_client -connect $site:443 -servername $site < /dev/null 2>/dev/null | openssl x509 -noout -dates
    curl -I -k https://$site/ | head -1
done
```