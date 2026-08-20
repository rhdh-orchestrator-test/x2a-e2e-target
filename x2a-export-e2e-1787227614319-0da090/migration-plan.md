# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database configuration, systemd service

- **cache**:
    - Description: Caching services configuration including Memcached and Redis
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef configuration file defining the run list and node attributes.
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider.
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Migration should use Ansible's `ufw` module to maintain the same security posture.
- **fail2ban Setup**: The Chef cookbook configures fail2ban for intrusion prevention. Migration should use Ansible's `fail2ban` module or templates.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Migration should use Ansible's `lineinfile` or templates to configure SSH.
- **SSL Certificate Management**: The Chef cookbook generates self-signed certificates for development. Migration should use Ansible's `openssl_*` modules.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No external vault integration is present in the current implementation

### Technical Challenges

- **Multi-site Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes. Migration should use Ansible loops and templates to achieve the same functionality.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for each site. Migration should use Ansible's `openssl_*` modules to generate certificates.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Migration should ensure proper service ordering and dependencies.
- **Python Environment Management**: The Chef cookbook creates and manages Python virtual environments. Migration should use Ansible's `pip` module with virtualenv support.

### Migration Order

1. **cache** (low risk, standalone): Migrate the caching services first as they have the fewest dependencies.
2. **nginx-multisite** (moderate complexity): Migrate the Nginx configuration next, as it provides the web server infrastructure.
3. **fastapi-tutorial** (high complexity): Migrate the FastAPI application last, as it depends on both the web server and database.

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems.
2. The Vagrant development environment will be maintained for testing.
3. Self-signed certificates are acceptable for development, but production deployment may require integration with Let's Encrypt or other certificate authorities.
4. The current security posture (firewall, fail2ban, SSH hardening) will be maintained.
5. The current hardcoded credentials will be replaced with Ansible Vault or another secrets management solution.
6. The FastAPI application source code will continue to be pulled from the same Git repository.
7. The PostgreSQL database schema and user setup will remain the same.
8. Redis and Memcached configurations will maintain the same performance characteristics.