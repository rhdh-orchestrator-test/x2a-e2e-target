---
source-path: chef-and-ansible
---

# Migration Plan: poodle_fix

**TLDR**: This is already an Ansible playbook that fixes the POODLE SSL vulnerability in Apache by enforcing TLSv1.2 and disabling older protocols. It updates the Apache SSL configuration and restarts both Apache and SSH services.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache2**: Web server with SSL configuration
  - Location/Path: /etc/apache2/mods-available/ssl.conf
  - Key Config: SSLProtocol set to "-all +TLSv1.2"

## File Structure

```
poodle_fix.yml
tests/ssh_profile.rb
tests/website_https_verify.rb
```

## Module Explanation

The playbook performs operations in this order:

1. **Fix SSL in Apache** (`poodle_fix.yml`):
   - Updates the Apache SSL configuration to disable vulnerable SSL protocols
   - Modifies /etc/apache2/mods-available/ssl.conf
   - Changes SSLProtocol directive to only allow TLSv1.2 and disable all other protocols
   - Resources: replace (1)

2. **Handlers** (`poodle_fix.yml`):
   - Restarts Apache2 service after configuration changes
   - Restarts SSH service after configuration changes
   - Resources: service (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: apache2, openssh-server
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: 0 credentials detected across 1 file

No credentials or secrets were detected in this playbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (*)

**Templates rendered**: None (uses replace module instead)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
systemctl status sshd

# Configuration validation
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf  # Should show "SSLProtocol -all +TLSv1.2"
apache2ctl -t  # Check Apache config syntax

# SSL/TLS protocol verification
openssl s_client -connect localhost:443 -ssl3 || echo "SSLv3 disabled (good)"
openssl s_client -connect localhost:443 -tls1 || echo "TLSv1.0 disabled (good)"
openssl s_client -connect localhost:443 -tls1_1 || echo "TLSv1.1 disabled (good)"
openssl s_client -connect localhost:443 -tls1_2 | grep "Protocol"  # Should show TLSv1.2

# Web server functionality
curl -k https://localhost/  # Verify site is accessible
curl -v -k https://localhost/ 2>&1 | grep "TLS"  # Verify TLS version

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
journalctl -u apache2 -f
journalctl -u sshd -f

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache
lsof -i :443

# POODLE vulnerability test
nmap --script ssl-enum-ciphers -p 443 localhost  # Should not show SSLv3 ciphers
```