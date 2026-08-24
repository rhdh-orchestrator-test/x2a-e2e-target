# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration
- SSL certificate management requires special attention

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW
    - Verification: Contains recipes/default.rb that includes security, nginx, ssl, and sites recipes

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration
    - Verification: Contains recipes/default.rb that configures Memcached and Redis

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management
    - Verification: Contains recipes/default.rb that sets up the FastAPI application environment

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration data including Nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the development VM configuration using Fedora 42

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role from Galaxy or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` or DavidWittman.redis role

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's `firewalld` or `ufw` modules
- **fail2ban Configuration**: Migrate fail2ban configuration to use Ansible's template module
- **SSH Hardening**: Migrate SSH security settings (disable root login, password authentication)
- **Sysctl Security Settings**: Migrate sysctl security configurations
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Consider using Ansible's `openssl_*` modules or integrating with Let's Encrypt via `geerlingguy.certbot`
- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes needs to be replicated using Ansible's templating system
- **Service Dependencies**: Ensuring proper ordering of service deployments (e.g., PostgreSQL before FastAPI application)
- **Python Environment Management**: Replicating the Python virtual environment setup and dependency installation

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Create base Nginx role with templates for configuration
   - Add SSL certificate management
   - Implement security hardening (fail2ban, firewall)

2. **cache** (Priority 2): Supporting services
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3): Application layer
   - PostgreSQL database setup
   - Python application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to use Fedora or a similar Linux distribution
2. Self-signed certificates are acceptable for development, but production may require proper certificates
3. The current security configurations are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL password policies are acceptable (though they should be moved to Ansible Vault)
6. The current service user configurations (www-data for Nginx, postgres for PostgreSQL) are appropriate for the target environment
7. The Vagrant development environment will be maintained, but Chef will be replaced with Ansible for provisioning