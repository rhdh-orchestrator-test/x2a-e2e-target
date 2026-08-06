# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

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
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file containing the run list and node attributes for Nginx sites, SSL, and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Defines the Vagrant VM configuration using Fedora 42 with port forwarding and networking setup.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **Firewall Configuration**: The current setup uses UFW for firewall management. Migration should use the `ansible.posix.firewalld` module for Fedora or `community.general.ufw` module for Ubuntu.
- **Fail2ban Integration**: Current setup configures fail2ban for intrusion prevention. Use Ansible to manage fail2ban configuration.
- **SSH Hardening**: The current setup disables root login and password authentication. Implement using the `ansible.posix.sshd_config` module.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Use Ansible's `community.crypto` collection for certificate management.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Consider using Ansible Vault for storing these secrets

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates Nginx site configurations based on node attributes. Ansible templates will need to replicate this dynamic behavior.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. Ansible will need to handle certificate generation and management.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible handlers and wait_for modules will be needed to ensure proper service startup order.
- **Platform Compatibility**: The current setup supports both Debian/Ubuntu and RHEL/CentOS/Fedora. Ansible playbooks will need to handle package and service differences between these platforms.

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement security configurations
   - Set up SSL certificate generation
   - Configure virtual hosts

2. **cache cookbook** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial cookbook** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy Python application from Git
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution.
2. Self-signed certificates are acceptable for development; production would require proper certificates.
3. The same security hardening measures (fail2ban, firewall, SSH hardening) are required in the Ansible implementation.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current directory structure and file organization in the target environment will be maintained.
6. The Vagrant setup is primarily for development/testing and may not be required in the final Ansible implementation.
7. No custom modules or plugins are required beyond standard Ansible modules and community collections.