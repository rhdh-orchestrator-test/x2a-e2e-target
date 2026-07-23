# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration scope includes 3 Chef cookbooks with moderate complexity. Based on the repository analysis, we estimate a 2-3 week timeline for complete migration, with the most complex components being the Nginx multi-site configuration and security hardening.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration data including run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>=18.04) and CentOS (>=7.0), with Fedora 42 used in the Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or `ansible.builtin.package` module
- **memcached (~> 6.0)**: Replace with Ansible `memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible `redis` role or direct package installation
- **Chef embedded resources**: Replace with equivalent Ansible modules:
  - `package` → `ansible.builtin.package`
  - `service` → `ansible.builtin.service`
  - `template` → `ansible.builtin.template`
  - `file` → `ansible.builtin.file`
  - `directory` → `ansible.builtin.file` with `state: directory`
  - `execute` → `ansible.builtin.command` or `ansible.builtin.shell`
  - `cookbook_file` → `ansible.builtin.copy`

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should use Ansible's `community.crypto.openssl_*` modules
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to Ansible's `community.general.ufw` module
  - Default deny policy with specific allows for SSH, HTTP, HTTPS

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migrate to Ansible's `ansible.posix.sshd_config` module

- **Fail2Ban Configuration**:
  - Fail2ban is installed and configured
  - Migrate to Ansible's `community.general.fail2ban` module

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials hardcoded in FastAPI recipe (`fastapi`/`fastapi_password`)
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current implementation uses Chef templates to generate site configurations
  - Ansible will need to replicate the dynamic site generation based on variables
  - Solution: Use Ansible's template module with Jinja2 templates

- **SSL Certificate Generation**:
  - Self-signed certificates are generated with OpenSSL commands
  - Solution: Use Ansible's `community.crypto.openssl_certificate` module

- **System Hardening**:
  - Multiple security configurations are applied (sysctl, SSH, firewall)
  - Solution: Consider using hardening roles from Ansible Galaxy (e.g., `dev-sec.ssh-hardening`)

- **Service Orchestration**:
  - The current setup has interdependent services (Nginx depends on SSL certificates)
  - Solution: Use Ansible handlers and proper task ordering

### Migration Order

1. **cache cookbook** (Priority 1 - low complexity)
   - Simple package installations and configurations
   - Good starting point to establish patterns

2. **fastapi-tutorial cookbook** (Priority 2 - moderate complexity)
   - Python application deployment
   - PostgreSQL database setup
   - Systemd service configuration

3. **nginx-multisite cookbook** (Priority 3 - highest complexity)
   - Multiple interdependent recipes
   - Security configurations
   - SSL certificate generation
   - Virtual host configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates
3. The current security configurations are appropriate and should be maintained in the Ansible version
4. The Vagrant development environment will be maintained but migrated to use Ansible provisioner
5. No changes to the application architecture are planned during migration
6. The FastAPI application repository URL will remain accessible
7. Redis and Memcached configurations will remain similar (no major version changes or configuration differences)
8. The migration will maintain the same level of idempotence as the current Chef implementation