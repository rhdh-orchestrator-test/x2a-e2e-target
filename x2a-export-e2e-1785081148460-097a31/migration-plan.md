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
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Manages Chef cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration data including Nginx site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42) with port forwarding and networking

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (18.04+) and CentOS (7.0+), with Fedora 42 used in the Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or `ansible.builtin.package` module + templates
- **memcached (~> 6.0)**: Replace with Ansible `memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible `redis` role or direct package installation with custom configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Migration should use Ansible's `ufw` module to maintain identical rules.
- **fail2ban Setup**: The Chef cookbook configures fail2ban for intrusion prevention. Migration should use Ansible's `fail2ban` module.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Migration should maintain these security settings using Ansible's `lineinfile` or templates.
- **SSL Certificate Management**: Self-signed certificates are generated for each virtual host. Migration should use Ansible's `openssl_*` modules to generate equivalent certificates.
- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes. The Ansible equivalent will need to use loops with templates to achieve the same functionality.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for each site. Ansible will need to use the `openssl_*` modules to replicate this behavior.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and Nginx depends on the SSL certificates. These dependencies need to be properly managed in Ansible.
- **Idempotent Execution**: Several Chef resources use `not_if` guards to ensure idempotency. Equivalent Ansible conditionals will be needed.

### Migration Order

1. **cache cookbook** (low complexity): Simple package installations and configuration files
2. **nginx-multisite cookbook** (moderate complexity): Core web server functionality with multiple sites
3. **fastapi-tutorial cookbook** (moderate complexity): Application deployment with database dependencies

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata.
2. The Vagrant development environment will be maintained for testing.
3. The current security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution.
4. Self-signed certificates are acceptable for the migrated solution (no Let's Encrypt or other CA integration required).
5. The PostgreSQL and Redis passwords currently hardcoded will need to be secured in the Ansible migration.
6. The FastAPI application source will continue to be pulled from the GitHub repository specified in the cookbook.