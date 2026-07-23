# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, fail2ban integration, UFW firewall configuration, security hardening

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file containing the run list and node attributes for the deployment.
- `solo.rb`: Chef configuration file specifying cookbook paths and logging settings.
- `Vagrantfile`: Defines the development VM using Vagrant with Fedora 42, network configuration, and port forwarding.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef, install dependencies, and run the Chef recipes.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package management

### Security Considerations

- **Firewall Configuration**: The current setup uses UFW for firewall management. Ansible has modules for both UFW and firewalld.
- **fail2ban Integration**: The setup includes fail2ban configuration for intrusion prevention. This will need to be migrated to Ansible tasks.
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) need to be preserved.
- **SSL Certificate Management**: Self-signed certificates are generated for development. Consider using Ansible's `community.crypto` collection.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI cookbook (`fastapi`/`fastapi_password`)
  - No Chef Vault or encrypted data bags are used, but these credentials should be moved to Ansible Vault

### Technical Challenges

- **SSL Certificate Generation**: The current setup generates self-signed certificates. This will need to be replicated in Ansible using the `community.crypto` collection.
- **Multi-site Configuration**: The Nginx configuration supports multiple virtual hosts with dynamic configuration. This will require careful templating in Ansible.
- **Security Hardening**: The comprehensive security configurations (sysctl, fail2ban, UFW) will need to be carefully migrated to maintain the same security posture.
- **Database Setup**: PostgreSQL database and user creation will need to be migrated to Ansible's PostgreSQL modules.

### Migration Order

1. **cache** (low risk, moderate value): Start with the simplest cookbook that handles Memcached and Redis configuration.
2. **nginx-multisite** (moderate complexity): Next, migrate the Nginx configuration with its security components.
3. **fastapi-tutorial** (high complexity): Finally, migrate the application deployment with its database dependencies.

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based systems, with possible support for Ubuntu/Debian.
2. The development workflow will continue to use Vagrant for local testing.
3. Self-signed certificates are acceptable for development, but production environments may require integration with Let's Encrypt or other certificate authorities.
4. The current security posture (fail2ban, UFW, SSH hardening) needs to be maintained in the Ansible implementation.
5. The current directory structure and file organization in the web server document roots will be preserved.
6. The FastAPI application will continue to be deployed from the same Git repository.
7. PostgreSQL and Python version requirements will remain the same.
8. Redis and Memcached configurations (ports, memory allocation) will remain unchanged.