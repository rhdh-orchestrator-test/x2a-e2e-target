# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible equivalents
- Security configurations need careful migration to maintain hardening standards

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
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef configuration data including the run list and node attributes for Nginx sites and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (18.04+) and CentOS (7.0+), with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration

### Security Considerations

- **Firewall Configuration**: The current implementation uses UFW. Migration should maintain equivalent firewall rules using either:
  - Ansible's `ufw` module for Ubuntu targets
  - Ansible's `firewalld` module for CentOS/RHEL targets

- **Fail2ban Configuration**: Current Chef cookbook configures fail2ban for intrusion prevention. Ansible migration should:
  - Install fail2ban package
  - Deploy equivalent jail configuration
  - Ensure service is enabled and running

- **SSL/TLS Management**: The current implementation generates self-signed certificates. Migration options:
  - Use Ansible's `openssl_*` modules for self-signed certificates
  - Integrate with Let's Encrypt using Ansible's `acme_certificate` module for production environments

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in fastapi-tutorial cookbook: username "fastapi" with password "fastapi_password"
  - Consider using Ansible Vault for storing these credentials securely

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes. Ansible implementation will need to:
  - Use templates with Jinja2 syntax instead of ERB
  - Maintain the same dynamic site generation capability
  - Ensure proper SSL certificate handling

- **Service Orchestration**: The current implementation has interdependent services (Nginx, PostgreSQL, Redis, FastAPI application). Ansible migration must:
  - Maintain correct service start order
  - Handle service notifications for configuration changes
  - Ensure idempotent execution

- **Python Environment Management**: The FastAPI application uses Python virtual environments. Ansible migration should:
  - Use Ansible's `pip` module with virtualenv support
  - Ensure proper environment variable handling for the application

### Migration Order

1. **cache** (Priority 1): Relatively simple cookbook with standard Redis and Memcached configurations
2. **nginx-multisite** (Priority 2): Core infrastructure component with security configurations
3. **fastapi-tutorial** (Priority 3): Application deployment with database dependencies

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL systems.
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates.
3. The current security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution.
4. The Vagrant development environment should be maintained for testing the Ansible playbooks.
5. The FastAPI application source code will remain at the same GitHub repository.
6. The PostgreSQL database schema and user setup should remain the same.
7. Redis authentication is required in the migrated solution.
8. The Nginx site configurations and document roots should be preserved.