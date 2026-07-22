# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **fastapi-tutorial**:
    - Description: FastAPI Python application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: SSL certificate generation, fail2ban integration, UFW firewall configuration, multiple virtual hosts

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file that defines the run list and node attributes.
- `solo.rb`: Chef configuration file for Chef Solo.
- `Vagrantfile`: Defines the development environment using Vagrant with Fedora 42.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for each site. Migration should use ansible.builtin.openssl_* modules.
- **Firewall Configuration**: UFW is configured with specific rules. Use ansible.posix.ufw module.
- **Fail2ban Integration**: Fail2ban is configured for intrusion prevention. Use community.general.fail2ban module.
- **SSH Hardening**: SSH configuration disables root login and password authentication. Use ansible.posix.ssh_config module.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi`/`fastapi_password`)
  - No external vault integration is present in the current implementation
  - Total credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation uses templates to generate site configurations. Ansible will need to replicate this dynamic site generation.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. Ansible will need to handle certificate generation and management.
- **System Hardening**: Multiple security configurations are applied. Ansible will need to replicate these security measures.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible will need to manage these dependencies.

### Migration Order

1. **cache** (low risk, foundational service)
   - Simple package installations and configurations
   - Minimal dependencies

2. **nginx-multisite** (moderate complexity)
   - Core web server functionality
   - Security configurations
   - SSL certificate management

3. **fastapi-tutorial** (high complexity, application-specific)
   - Depends on PostgreSQL
   - Requires Git repository deployment
   - Python environment setup
   - Systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based systems, with potential support for Ubuntu/Debian.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
3. The same security hardening measures should be applied in the Ansible implementation.
4. The FastAPI application source code will remain at the same GitHub repository.
5. The current Redis and PostgreSQL passwords are for development only and should be replaced with Ansible Vault variables.
6. The Vagrant development environment should be preserved but updated to use Ansible provisioning.