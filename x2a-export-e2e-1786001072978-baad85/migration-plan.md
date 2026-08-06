# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database, systemd service

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists external dependencies (nginx, memcached, redisio)
- `solo.json`: Chef run list and configuration data for the cookbooks
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM (Fedora 42) with networking and provisioning
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant VM

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or the community.general collection's nginx modules
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` role from community.general collection
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` role from community.general collection

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt.
- **Firewall Configuration**: UFW rules need to be migrated to equivalent Ansible UFW module tasks.
- **Fail2ban Configuration**: Configuration needs to be migrated to Ansible tasks.
- **SSH Hardening**: SSH security configurations need to be preserved in the Ansible playbooks.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - No external vault integration detected, passwords are hardcoded in recipes

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx sites based on configuration data needs to be preserved in Ansible.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated in Ansible.
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations, particularly for the FastAPI application which depends on PostgreSQL.
- **Security Hardening**: Comprehensive security configurations need to be maintained across the migration.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, ufw)
   - Configure multi-site setup

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy application from Git
   - Configure Python environment
   - Create systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (no requirement for Let's Encrypt integration).
3. The same security hardening measures are required in the Ansible implementation.
4. The FastAPI application source repository will remain available at the specified URL.
5. The directory structure for web content and application deployment can remain the same.
6. No additional monitoring or logging requirements beyond what's in the current implementation.
7. The passwords and security credentials in the current implementation can be reused (no requirement to rotate credentials).