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
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

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

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef node configuration with run list and attributes for Nginx sites and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's `ufw` module or `firewalld` module depending on target OS.
- **Fail2ban Setup**: The Chef cookbook configures fail2ban. Migration should use Ansible's `template` module to create fail2ban configuration.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Migration should use Ansible's `lineinfile` or `template` module to configure SSH.
- **SSL Certificate Management**: The Chef cookbook generates self-signed certificates. Migration should use Ansible's `openssl_certificate` module.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123" (hardcoded)
  - PostgreSQL password in fastapi-tutorial cookbook: "fastapi_password" (hardcoded)
  - Both should be migrated to Ansible Vault or other secret management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes. Migration should use Ansible templates with variable substitution.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates. Migration should use Ansible's `openssl_certificate` module with similar parameters.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Migration should ensure proper service ordering in Ansible.
- **Idempotent Execution**: Some Chef resources use `not_if` guards to ensure idempotence. Migration should use Ansible's `creates`, `when`, or `changed_when` directives.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Break into separate roles: nginx-base, nginx-ssl, nginx-security
   - Create templates for nginx.conf, site configurations, and security settings

2. **cache** (Priority 2): Independent service with moderate complexity
   - Create separate roles for memcached and redis
   - Use Ansible Vault for Redis password

3. **fastapi-tutorial** (Priority 3): Application deployment with database dependencies
   - Create roles for PostgreSQL and FastAPI application
   - Use Ansible Vault for database credentials
   - Ensure proper service ordering and dependencies

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based on the current configuration.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
3. The current security configurations (fail2ban, ufw, SSH hardening) should be maintained in the Ansible solution.
4. The Vagrant development environment should be preserved with equivalent functionality.
5. The FastAPI application source will continue to be pulled from the GitHub repository.
6. The current Redis and Memcached configurations are sufficient and don't require additional tuning.
7. The PostgreSQL database setup is minimal and doesn't include advanced features like replication or backups.