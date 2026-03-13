# Migration Plan: Ansible SSL Poodle Fix Playbook

**TLDR**: This is already an Ansible playbook that mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. It also restarts both Apache and SSH services after making the change.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache2**: Web server with SSL configuration
  - Location/Path: /etc/apache2/mods-available/ssl.conf
  - Key Config: SSLProtocol set to "-all +TLSv1.2" (disables all protocols except TLSv1.2)

- **SSHD**: SSH server that is restarted after configuration changes
  - No direct configuration changes, but service is restarted

## File Structure

```
chef-and-ansible/poodle_fix.yml
```

This is already an Ansible playbook, not a Chef cookbook. The file structure is simple with just a single YAML file containing the playbook.

## Module Explanation

The playbook performs operations in this order:

1. **SSL Configuration Fix** (`chef-and-ansible/poodle_fix.yml`):
   - Targets hosts in the "myhost" group
   - Runs as root user (become: yes)
   - Uses the `replace` module to modify Apache SSL configuration
   - Changes the SSLProtocol line to disable all protocols except TLSv1.2
   - Path: /etc/apache2/mods-available/ssl.conf
   - Pattern: Replaces any line starting with "SSLProtocol" with "SSLProtocol -all +TLSv1.2"
   - Resources: replace (1)
   - Notifications: Triggers two handlers - "Restart apache2" and "Restart sshd"

2. **Service Handlers** (`chef-and-ansible/poodle_fix.yml`):
   - Handler: "Restart apache"
     - Uses ansible.builtin.service module
     - Restarts the apache2 service
   - Handler: "Restart sshd"
     - Uses ansible.builtin.service module
     - Restarts the sshd service
   - Resources: service (2)

## Dependencies

**System package dependencies**: apache2, openssh-server (implied by the services being restarted)
**Service dependencies**: apache2, sshd

## Checks for the Migration

**Files to verify**:
- /etc/apache2/mods-available/ssl.conf (should contain "SSLProtocol -all +TLSv1.2")

**Service endpoints to check**:
- Apache HTTPS port (typically 443)
- SSH port (typically 22)

## Pre-flight checks:
```bash
# Check Apache SSL configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf
# Should show: SSLProtocol -all +TLSv1.2

# Service status
systemctl status apache2
systemctl status sshd

# Test SSL configuration with OpenSSL
openssl s_client -connect localhost:443 -tls1_2
# Should connect successfully

openssl s_client -connect localhost:443 -ssl3
# Should fail with "wrong version number" or similar

openssl s_client -connect localhost:443 -tls1
# Should fail with "wrong version number" or similar

openssl s_client -connect localhost:443 -tls1_1
# Should fail with "wrong version number" or similar

# Check for POODLE vulnerability
nmap --script ssl-poodle -p 443 localhost
# Should report "not vulnerable"

# Verify HTTPS connectivity
curl -k https://localhost/
# Should return the website content

# Check SSH connectivity
ssh -v localhost exit
# Should connect successfully

# Check logs for any errors
tail -f /var/log/apache2/error.log
journalctl -u apache2 -f
journalctl -u sshd -f
```

Note: Since this is already an Ansible playbook and not a Chef cookbook, no actual migration is needed. The playbook is already designed to mitigate the POODLE vulnerability by restricting SSL/TLS protocols to only TLSv1.2 in Apache's configuration.