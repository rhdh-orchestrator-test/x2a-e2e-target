# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security hardening practices.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard web server, caching, and application deployment patterns
- Security hardening that follows common practices
- Self-contained development environment using Vagrant

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the Chef run list and configuration attributes for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development and testing
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Ansible migration should use the `ansible.posix.firewalld` or `community.general.ufw` modules to implement equivalent rules.
- **fail2ban Setup**: The cookbook configures fail2ban with a custom jail configuration. Ansible should use the `community.general.fail2ban` module or direct configuration file management.
- **SSH Hardening**: The cookbook disables root login and password authentication. Ansible should use the `ansible.posix.sshd_config` module to apply the same settings.
- **System Hardening**: The cookbook applies sysctl security settings. Ansible should use the `ansible.posix.sysctl` module to apply equivalent settings.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL database credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi`/`fastapi_password`)
  - SSL certificates are generated on the fly with self-signed certificates

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically generates site configurations based on attributes. Ansible will need to use loops with templates to achieve the same functionality.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for development. Ansible will need to use the `community.crypto.openssl_*` modules to generate equivalent certificates or integrate with Let's Encrypt for production.
- **Redis Configuration Hack**: The Chef cookbook includes a Ruby block to modify the Redis configuration file after installation. Ansible will need to use the `lineinfile` or `replace` modules to achieve the same result, or preferably use a template with the correct configuration from the start.
- **FastAPI Application Deployment**: The Chef cookbook clones a Git repository and sets up a Python virtual environment. Ansible will need to use the `git`, `pip`, and `systemd` modules to achieve the same result.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, firewall, sysctl)
   - Add multi-site configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Address the Redis configuration hack

3. **fastapi-tutorial** (moderate complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment from Git
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution.
2. The self-signed SSL certificates are for development only and may be replaced with proper certificates in production.
3. The hardcoded passwords in the Chef cookbooks are for development only and should be replaced with Ansible Vault variables in production.
4. The Vagrant development environment will be maintained, but with Ansible provisioning instead of Chef.
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
6. The current security hardening practices are sufficient and should be maintained in the Ansible roles.
7. The multi-site Nginx configuration pattern will be preserved in the Ansible roles.