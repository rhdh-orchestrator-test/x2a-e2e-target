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
- `solo.json`: Chef configuration data including Nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42) with port forwarding and networking

### Target Details

Based on the source repository analysis:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or `ansible.builtin.package` module + templates
- **memcached (~> 6.0)**: Replace with Ansible `memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible `redis` role or direct package installation
- **Python 3 and venv**: Use Ansible `ansible.builtin.package` and `pip` modules

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Migration should use Ansible's `ufw` module to maintain identical rules.
- **fail2ban Setup**: The Chef cookbook installs and configures fail2ban. Use Ansible's `fail2ban` module or template configuration files.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Use Ansible's `lineinfile` or templates to configure SSH.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Use Ansible's `openssl_certificate` module to generate certificates.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes. Ansible will need to use templates with loops to achieve the same functionality.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. Ansible will need to use the `openssl_certificate` module with proper conditionals.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible handlers and proper ordering will be needed.
- **Idempotent Execution**: Several Chef resources use `not_if` guards to ensure idempotency. Ansible tasks will need similar conditionals.

### Migration Order

1. **cache cookbook** (Low complexity, foundational service)
   - Basic package installation and configuration
   - Minimal dependencies on other services

2. **nginx-multisite cookbook** (Medium complexity, core infrastructure)
   - Base Nginx installation and configuration
   - Security hardening (fail2ban, firewall)
   - SSL certificate generation
   - Virtual host configuration

3. **fastapi-tutorial cookbook** (High complexity, application layer)
   - Depends on PostgreSQL database
   - Requires Python environment setup
   - Involves Git repository deployment
   - Requires systemd service configuration

### Assumptions

1. The target environment will continue to be either Ubuntu (>= 18.04) or CentOS (>= 7.0)
2. Self-signed certificates are acceptable for the migrated solution (no Let's Encrypt integration required)
3. The same security hardening measures should be maintained in the Ansible solution
4. The Vagrant development environment should be preserved with the same networking configuration
5. The FastAPI application source code will remain available at the same Git repository URL
6. The PostgreSQL database schema does not require migration, only the database server configuration
7. Redis and Memcached configurations should maintain the same performance characteristics
8. No additional monitoring or logging requirements beyond what's in the current Chef implementation