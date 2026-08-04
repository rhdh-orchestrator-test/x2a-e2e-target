# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

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
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Contains node attributes including Nginx site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development/testing
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module with custom templates
- **PostgreSQL**: Replace with Ansible postgresql_* modules or community.postgresql collection

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Migration should use Ansible's ufw module to maintain identical rules.
- **fail2ban Setup**: The cookbook configures fail2ban with custom jail settings. Migration should use Ansible's template module to create equivalent configuration.
- **SSH Hardening**: The cookbook disables root login and password authentication. Migration should use Ansible's lineinfile or template module to configure sshd_config.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Migration should use Ansible's openssl_* modules to generate equivalent certificates.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No external vault integration is present in the current implementation

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on node attributes. The Ansible equivalent will need to use loops with the template module.
- **SSL Certificate Generation**: The cookbook generates self-signed certificates for each site. Ansible will need to use the openssl_certificate module with proper idempotency checks.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible handlers and meta dependencies will need to be configured to ensure proper service ordering.
- **Redis Configuration**: The cookbook includes a custom Ruby block to modify Redis configuration. Ansible will need to use either lineinfile or a custom template to achieve the same result.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role with templates
   - Add SSL certificate generation
   - Add security configurations (fail2ban, ufw)
   - Add site configuration templates

2. **cache** (low complexity, independent service)
   - Create Memcached role
   - Create Redis role with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Create PostgreSQL role
   - Create Python application deployment role
   - Configure systemd service

### Assumptions

1. The current Chef setup assumes a single-server deployment model where all services (Nginx, Redis, Memcached, PostgreSQL, FastAPI) run on the same host.
2. SSL certificates are self-signed and generated on the fly, suggesting a development or internal environment rather than production.
3. Security configurations are basic and focused on SSH hardening, firewall rules, and fail2ban.
4. The FastAPI application is pulled directly from a GitHub repository rather than being built and deployed from a CI/CD pipeline.
5. No monitoring or logging solutions are configured in the current setup.
6. No backup strategy is defined for PostgreSQL or Redis data.
7. The Redis configuration contains a workaround ("fix_redis_config" Ruby block) that may need special attention during migration.
8. The Vagrant setup suggests this is primarily a development environment configuration.