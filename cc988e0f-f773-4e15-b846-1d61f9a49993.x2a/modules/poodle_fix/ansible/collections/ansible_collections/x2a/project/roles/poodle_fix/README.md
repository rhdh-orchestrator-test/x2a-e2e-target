# Ansible Role: poodle_fix

## Description

This role fixes the POODLE (Padding Oracle On Downgraded Legacy Encryption) SSL vulnerability by configuring Apache to use only secure TLS protocols. It modifies the Apache SSL configuration to disable SSLv3 and enable only TLSv1.2 and TLSv1.3.

**Important:** This is a configuration-only role. Apache must already be installed on the target system. The role will fail with a clear error message if Apache is not present.

## Requirements

- **Apache2/httpd must be installed** on the target system before running this role
- Apache SSL module must be enabled
- Root/sudo access on target systems
- Debian/Ubuntu or RHEL/CentOS-based systems

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# Path to Apache SSL configuration file
poodle_fix_apache_ssl_conf_path: /etc/apache2/mods-available/ssl.conf

# SSL/TLS protocols to enable (POODLE fix)
poodle_fix_apache_ssl_protocols: "-all +TLSv1.2 +TLSv1.3"

# Apache service name
poodle_fix_apache_service_name: apache2

# Backup configuration before changes
poodle_fix_apache_backup_config: true

# Restart Apache after configuration change
poodle_fix_apache_restart_required: true

# Secure logging for sensitive operations
poodle_fix_secure_logging: true
```

## Dependencies

None. However, Apache must be installed before running this role.

## Example Playbook

```yaml
---
- name: Apply POODLE fix to web servers
  hosts: webservers
  become: true
  roles:
    - role: x2a.project.poodle_fix
      vars:
        poodle_fix_apache_service_name: httpd  # For RHEL/CentOS
        poodle_fix_apache_ssl_conf_path: /etc/httpd/conf.d/ssl.conf
```

### With Apache Installation

```yaml
---
- name: Install Apache and apply POODLE fix
  hosts: webservers
  become: true
  tasks:
    - name: Install Apache on Debian/Ubuntu
      ansible.builtin.apt:
        name: apache2
        state: present
      when: ansible_os_family == 'Debian'

    - name: Install Apache on RHEL/CentOS
      ansible.builtin.yum:
        name: httpd
        state: present
      when: ansible_os_family == 'RedHat'

  roles:
    - role: x2a.project.poodle_fix
      vars:
        poodle_fix_apache_service_name: "{{ 'httpd' if ansible_os_family == 'RedHat' else 'apache2' }}"
        poodle_fix_apache_ssl_conf_path: "{{ '/etc/httpd/conf.d/ssl.conf' if ansible_os_family == 'RedHat' else '/etc/apache2/mods-available/ssl.conf' }}"
```

## Platform Support

This role supports:
- Debian/Ubuntu (apache2)
- RHEL/CentOS (httpd) - requires variable overrides

## Pre-flight Checks

Before applying the role:

```bash
# Verify Apache is installed and SSL module exists
ansible target_hosts -m ansible.builtin.command -a "apache2 -v"
ansible target_hosts -m ansible.builtin.stat -a "path=/etc/apache2/mods-available/ssl.conf"

# Check current SSL configuration
ansible target_hosts -m ansible.builtin.command -a "grep SSLProtocol /etc/apache2/mods-available/ssl.conf"
```

## Behavior

The role performs these checks:

1. **File existence check**: Verifies the Apache SSL configuration file exists
2. **Service existence check**: Gathers service facts to verify Apache service is present
3. **Configuration update**: Modifies SSL protocol settings only if file exists
4. **Service restart**: Restarts Apache only if the service exists and changes were made

The role will **fail** with a clear error message if:
- The Apache SSL configuration file does not exist (Apache not installed)
- This prevents silent failures and ensures the role only runs on systems with Apache

## Post-deployment Verification

After applying the role:

```bash
# Verify Apache configuration syntax
ansible target_hosts -m ansible.builtin.command -a "apache2ctl configtest"

# Verify Apache is running
ansible target_hosts -m ansible.builtin.service -a "name=apache2 state=started"

# Verify SSL protocol configuration
ansible target_hosts -m ansible.builtin.command -a "grep SSLProtocol /etc/apache2/mods-available/ssl.conf"

# Test SSL/TLS protocols using openssl (from control node)
openssl s_client -connect target_host:443 -ssl3    # Should fail
openssl s_client -connect target_host:443 -tls1_2  # Should succeed
```

## Security Notes

- This role creates a backup of the SSL configuration file before modification
- The default configuration disables all SSL protocols and enables only TLSv1.2 and TLSv1.3
- Apache is automatically restarted after configuration changes (can be disabled with `poodle_fix_apache_restart_required: false`)
- The role will not create a configuration file if it doesn't exist (fails loudly instead)

## License

Apache-2.0

## Author Information

Migrated from legacy playbook to modern Ansible role structure.
