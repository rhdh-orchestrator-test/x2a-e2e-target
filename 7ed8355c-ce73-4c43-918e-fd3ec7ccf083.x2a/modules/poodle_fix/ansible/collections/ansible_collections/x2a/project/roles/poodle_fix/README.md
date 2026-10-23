# Ansible Role: poodle_fix

## Description

Fixes the POODLE SSL vulnerability (CVE-2014-3566) in Apache web server by disabling SSLv3 and enforcing modern TLS protocols.

This role:
- Configures Apache to disable SSLv3 protocol
- Enforces TLSv1.2 (or higher) for secure connections
- Backs up configuration files before modification
- Restarts Apache service to apply changes
- Optionally restarts SSHD service for additional security hardening
- Supports both Debian/Ubuntu (apache2) and RHEL/CentOS (httpd) systems

## Requirements

- Apache web server must be installed
- Apache SSL module must be enabled
- Root or sudo access required

## Role Variables

Available variables with their default values (see `defaults/main.yml`):

```yaml
# Apache SSL configuration
poodle_fix_apache_ssl_config_path: /etc/apache2/mods-available/ssl.conf
poodle_fix_ssl_protocol: '-all +TLSv1.2'

# Service management
poodle_fix_apache_service_name: apache2
poodle_fix_restart_apache: true
poodle_fix_restart_sshd: true

# Safety options
poodle_fix_backup_config: true
poodle_fix_validate_config: true
```

### Variable Details

- `poodle_fix_apache_ssl_config_path`: Path to Apache SSL configuration file. Automatically set based on OS family (Debian/Ubuntu vs RHEL/CentOS)
- `poodle_fix_ssl_protocol`: SSL protocol configuration string. Default disables all protocols and enables only TLSv1.2. Consider using `'-all +TLSv1.2 +TLSv1.3'` for modern systems
- `poodle_fix_apache_service_name`: Name of the Apache service. Automatically set based on OS family (apache2 vs httpd)
- `poodle_fix_restart_apache`: Whether to restart Apache after configuration change
- `poodle_fix_restart_sshd`: Whether to restart SSHD service (set to false if not needed)
- `poodle_fix_backup_config`: Whether to backup configuration file before modification
- `poodle_fix_validate_config`: Whether to validate Apache configuration before restarting

## Dependencies

This role requires the `ansible.posix` collection (see `requirements.yml`).

## Platform Support

- **Debian/Ubuntu**: apache2, /etc/apache2/ paths
- **RHEL/CentOS/Rocky/AlmaLinux**: httpd, /etc/httpd/ paths

The role automatically detects the OS family and uses appropriate paths and service names.

## Example Playbook

```yaml
---
- name: Fix POODLE vulnerability on web servers
  hosts: webservers
  become: true
  roles:
    - role: x2a.project.poodle_fix
```

### Custom SSL Protocol Configuration

```yaml
---
- name: Fix POODLE with TLSv1.2 and TLSv1.3
  hosts: webservers
  become: true
  roles:
    - role: x2a.project.poodle_fix
      vars:
        poodle_fix_ssl_protocol: '-all +TLSv1.2 +TLSv1.3'
```

### Skip SSHD Restart

```yaml
---
- name: Fix POODLE without SSHD restart
  hosts: webservers
  become: true
  roles:
    - role: x2a.project.poodle_fix
      vars:
        poodle_fix_restart_sshd: false
```

## Verification

After running this role, verify the fix:

```bash
# Test that SSLv3 is disabled (should fail)
openssl s_client -connect yourserver:443 -ssl3

# Test that TLSv1.2 works (should succeed)
openssl s_client -connect yourserver:443 -tls1_2

# Verify configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf  # Debian/Ubuntu
grep "SSLProtocol" /etc/httpd/conf.d/ssl.conf            # RHEL/CentOS

# Check Apache service status
systemctl status apache2  # Debian/Ubuntu
systemctl status httpd    # RHEL/CentOS
```

## Security Considerations

1. **TLS Version**: The default configuration enforces TLSv1.2. For modern systems, consider also enabling TLSv1.3 by setting `poodle_fix_ssl_protocol: '-all +TLSv1.2 +TLSv1.3'`

2. **Backup**: Configuration files are backed up by default before modification. Backups are stored with a timestamp suffix.

3. **SSHD Restart**: The role optionally restarts SSHD service. If this is not needed for your security posture, set `poodle_fix_restart_sshd: false`

4. **Testing**: Always test SSL/TLS configuration in a non-production environment first

## Migration Notes

This role was migrated from a standalone Ansible playbook. Key improvements:
- Fixed critical handler name mismatch bug from original
- Added cross-platform support (Debian/Ubuntu and RHEL/CentOS)
- Added configuration backup and validation
- Modernized with FQCN module names
- Added proper role structure and documentation
- Made all paths and service names configurable

## License

Apache-2.0

## Author Information

Migrated to Ansible role structure by x2a migration tooling.
