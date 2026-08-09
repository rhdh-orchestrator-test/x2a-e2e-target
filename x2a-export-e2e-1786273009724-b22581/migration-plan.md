# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site web application environment with FastAPI backend, Nginx web server, and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- Limited external dependencies (nginx, memcached, redisio)
- Some security configurations that need careful migration
- Credential management needs to be addressed

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, UFW)

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external dependencies with version constraints.
- `solo.json`: Chef configuration file defining the run list and node attributes. Contains site configurations and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines a Vagrant VM for development and testing with Fedora 42, port forwarding, and resource allocation.
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef, installs dependencies, and runs Chef Solo.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` role or community.general collection
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` role or community.general collection

### Security Considerations

- **SSL/TLS Configuration**: The nginx-multisite cookbook manages SSL certificates and private keys. Migration should maintain secure storage and deployment of certificates.
  - Migration approach: Use Ansible Vault for certificate storage or integrate with external certificate management systems.

- **fail2ban Configuration**: Security hardening with fail2ban needs to be preserved.
  - Migration approach: Use Ansible's fail2ban modules or community roles.

- **UFW Firewall Rules**: Security settings include UFW configuration.
  - Migration approach: Use Ansible's ufw module to maintain firewall configuration.

- **SSH Hardening**: SSH security settings (disable root login, password authentication).
  - Migration approach: Use Ansible's ssh_config module or security roles.

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - These should be migrated to Ansible Vault or an external secrets management system

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. This requires careful migration to maintain the same functionality.
  - Mitigation: Create a flexible Ansible role with templates that can handle multiple site configurations.

- **PostgreSQL Database Setup**: The fastapi-tutorial cookbook sets up a PostgreSQL database with specific user permissions.
  - Mitigation: Use Ansible's postgresql_* modules to manage database, users, and permissions.

- **Python Application Deployment**: The fastapi-tutorial cookbook manages a Python virtual environment and application deployment.
  - Mitigation: Create an Ansible role that handles Python application deployment with proper dependency management.

- **Redis Configuration Customization**: The cache cookbook includes a Ruby block to modify Redis configuration files after deployment.
  - Mitigation: Use Ansible templates with proper conditionals to generate correct Redis configuration directly.

### Migration Order

1. **cache** (Priority 1): Relatively simple cookbook with well-defined dependencies. Good starting point with lower complexity.
2. **nginx-multisite** (Priority 2): Core infrastructure component with security implications. Moderate complexity with templates and multiple site configurations.
3. **fastapi-tutorial** (Priority 3): Application deployment with database dependencies. Higher complexity due to application-specific configurations.

### Assumptions

1. The current Chef setup is functional and represents the desired state for the Ansible migration.
2. Self-signed certificates are currently used in development, but the production environment may use different certificate management.
3. The Vagrant environment is primarily for development/testing, and the production deployment may have different requirements.
4. No custom Chef resources or libraries are used beyond what's visible in the repository.
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and will remain available.
6. The current security configurations (fail2ban, UFW, SSH hardening) are sufficient and should be maintained in the Ansible migration.
7. The Redis and Memcached configurations are standard and don't have extensive customizations beyond what's visible in the cookbooks.
8. The PostgreSQL database setup is relatively simple and doesn't include complex replication or high availability configurations.