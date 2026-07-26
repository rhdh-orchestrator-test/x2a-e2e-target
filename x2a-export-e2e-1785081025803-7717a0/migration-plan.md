# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
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
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef configuration file containing the run list and node attributes for Nginx sites and security settings.
- `solo.rb`: Chef configuration file specifying file paths and log settings.
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding for HTTP/HTTPS.
- `vagrant-provision.sh`: Shell script that installs Chef and Berkshelf, then runs Chef Solo in the Vagrant VM.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **Firewall Configuration**: The nginx-multisite cookbook configures UFW firewall. Migration should use Ansible's `ufw` module.
- **Fail2ban Setup**: The cookbook configures fail2ban with custom jail settings. Migration should use Ansible's `fail2ban` module.
- **SSH Hardening**: The cookbook disables root login and password authentication. Migration should use Ansible's `lineinfile` module or the `ansible-hardening` role.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Migration should use Ansible's `openssl_*` modules.
- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi`/`fastapi_password`)
  - These should be migrated to Ansible Vault or an external secrets management solution

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on node attributes. This will require careful translation to Ansible templates and variables.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. This will need to be replicated using Ansible's `openssl_certificate` module.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. This dependency chain needs to be maintained in Ansible with proper handlers and notifications.
- **Redis Configuration Hack**: The cache cookbook includes a Ruby block to modify Redis configuration files after they're created. This will need special handling in Ansible.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add security hardening (fail2ban, ufw, sysctl)
   - Implement SSL certificate generation
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy Python application from Git
   - Configure virtual environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
3. The current hardcoded credentials will be replaced with Ansible Vault variables.
4. The Vagrant development environment will be maintained but converted to use Ansible provisioner instead of Chef.
5. The current directory structure with separate roles for each component will be maintained in the Ansible project.
6. The FastAPI application source code will continue to be pulled from the same Git repository.
7. No changes to the application configuration or behavior are required as part of the migration.