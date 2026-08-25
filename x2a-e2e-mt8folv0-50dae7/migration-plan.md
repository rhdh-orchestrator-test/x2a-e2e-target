# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration to maintain hardening standards

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, SSH hardening)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef Solo configuration file containing the run list and node attributes.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider.
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible Galaxy `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy `geerlingguy.redis` role

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's `ufw` module or `firewalld` module depending on the target OS.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Migration should use Ansible's `lineinfile` or `template` module to configure SSH.
- **fail2ban**: The Chef cookbook configures fail2ban. Migration should use Ansible's `template` module to configure fail2ban.
- **SSL/TLS Certificates**: Self-signed certificates are generated for development. Migration should use Ansible's `openssl_certificate` module.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be migrated to Ansible Vault or an external secrets management solution

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates virtual hosts based on node attributes. This pattern needs to be replicated in Ansible using loops and templates.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. This needs to be replicated in Ansible using the `openssl_certificate` module.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. This dependency needs to be managed in Ansible using handlers or the `meta` module.
- **Redis Configuration**: The Chef cookbook uses a custom Ruby block to modify Redis configuration. This needs to be replicated in Ansible using the `lineinfile` module or a custom template.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
2. **cache** (Priority 2): Supporting services that can be deployed independently
3. **fastapi-tutorial** (Priority 3): Application deployment that depends on the infrastructure

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions.
2. The Vagrant development environment will be maintained for testing.
3. Self-signed certificates are acceptable for development, but production deployment may require integration with Let's Encrypt or another certificate authority.
4. The current security hardening practices should be maintained or enhanced in the Ansible migration.
5. The current Redis and PostgreSQL passwords are for development only and will be replaced with secure passwords in production.