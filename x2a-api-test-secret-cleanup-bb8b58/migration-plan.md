# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment**: Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Multiple external dependencies (nginx, memcached, redis)
- Security configurations that need careful migration
- Database and application deployment that requires proper sequencing

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Provisioning script for Vagrant environment
- `Vagrantfile`: Vagrant configuration for development environment

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's firewalld or ufw modules based on target OS.
- **Fail2ban Setup**: Configuration needs to be migrated using Ansible templates.
- **SSH Hardening**: SSH configuration changes (disabling root login, password authentication) should be handled via Ansible's template module or lineinfile.
- **Sysctl Security Settings**: System security parameters need to be migrated using Ansible's sysctl module.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123" (hardcoded)
  - PostgreSQL credentials in fastapi-tutorial cookbook: username "fastapi" with password "fastapi_password" (hardcoded)
  - SSL certificates are generated on the fly, no pre-existing secrets
  - Total credentials detected: 2 sets of database credentials hardcoded in recipes

### Technical Challenges

- **SSL Certificate Generation**: Chef cookbook generates self-signed certificates. Ansible migration should use the openssl_* modules to replicate this functionality.
- **Custom Resource Migration**: The `lineinfile` custom resource in nginx-multisite needs to be replaced with Ansible's native lineinfile module.
- **Service Dependencies**: Ensuring proper ordering of service deployments, especially for the FastAPI application which depends on PostgreSQL.
- **Template Migration**: Several ERB templates need to be converted to Jinja2 format for Ansible.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Base Nginx installation
   - Security configurations
   - SSL certificate generation
   - Virtual host configuration

2. **cache** (low complexity, standalone service)
   - Memcached configuration
   - Redis installation and security

3. **fastapi-tutorial** (high complexity, application deployment)
   - PostgreSQL database setup
   - Python environment configuration
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (the Vagrantfile specifies Fedora 42).
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
3. The hardcoded credentials in the recipes will be replaced with Ansible Vault or another secrets management solution.
4. The same directory structure for web content and configuration files will be maintained.
5. The FastAPI application source will continue to be pulled from the same Git repository.
6. The current security configurations (fail2ban, ufw, sysctl) are appropriate for the target environment.
7. The Vagrant development environment will be maintained but provisioned with Ansible instead of Chef.