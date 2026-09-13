---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Multi-site nginx web server with SSL-enabled virtual hosts for 3 subdomains (test.cluster.local, ci.cluster.local, status.cluster.local), includes security hardening with fail2ban, UFW firewall, and SSH configuration.

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
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Creates document root directory for each site
     - Deploys static index.html file for each site
       - test.cluster.local: files/default/test/index.html → /opt/server/test/index.html
       - ci.cluster.local: files/default/ci/index.html → /opt/server/ci/index.html
       - status.cluster.local: files/default/status/index.html → /opt/server/status/index.html
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3)

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group for certificate management
   - Creates SSL certificate and private key directories: /etc/ssl/certs, /etc/ssl/private
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Generates self-signed SSL certificate for each site using OpenSSL
     - Sets certificate subject: /C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN={site_name}/emailAddress=admin@example.com
     - Sets private key permissions: 640, owner root:ssl-cert
   - Resources: package (1), group (1), directory (2), execute (3)

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Deploys nginx virtual host configuration for each site
       - Template: site.conf.erb → /etc/nginx/sites-available/{site_name}
       - Variables: server_name, document_root, ssl_enabled, cert_file, key_file
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

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. SSL certificates are self-signed and generated locally with hardcoded subject information.

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
- Ports: 80 (HTTP), 443 (HTTPS), 22 (SSH)
- Unix sockets: None

**Templates rendered**:
- fail2ban.jail.local.erb (1 time)
- nginx.conf.erb (1 time)
- security.conf.erb (1 time)
- sysctl-security.conf.erb (1 time)
- site.conf.erb (3 times: test.cluster.local, ci.cluster.local, status.cluster.local)

## Pre-flight checks:
```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status ssh

# Site: test.cluster.local
curl -I http://test.cluster.local
curl -I https://test.cluster.local
curl -s https://test.cluster.local | grep "Test Environment"
openssl s_client -connect test.cluster.local:443 -servername test.cluster.local < /dev/null | grep "CN=test.cluster.local"

# Site: ci.cluster.local
curl -I http://ci.cluster.local
curl -I https://ci.cluster.local
curl -s https://ci.cluster.local | grep "CI Environment"
openssl s_client -connect ci.cluster.local:443 -servername ci.cluster.local < /dev/null | grep "CN=ci.cluster.local"

# Site: status.cluster.local
curl -I http://status.cluster.local
curl -I https://status.cluster.local
curl -s https://status.cluster.local | grep "Status Environment"
openssl s_client -connect status.cluster.local:443 -servername status.cluster.local < /dev/null | grep "CN=status.cluster.local"

# SSL certificate validation
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -text -noout | grep -E "Subject:|Not After"
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -text -noout | grep -E "Subject:|Not After"
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -text -noout | grep -E "Subject:|Not After"

# Configuration validation
nginx -t
fail2ban-client status
ufw status
netstat -tulpn | grep -E ":80|:443|:22"
```