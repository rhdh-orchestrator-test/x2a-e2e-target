# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- Moderate number of external dependencies (nginx, memcached, redis)
- Security configurations that need careful migration
- Database integration with PostgreSQL

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services including Memcached and Redis
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Configuration data for Chef Solo, contains site configurations and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Defines the development VM configuration using Fedora 42.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, but the Vagrantfile uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile.
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **PostgreSQL**: Use Ansible postgresql_* modules from community.postgresql collection

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the nginx-multisite cookbook
  - Migration should use ansible.builtin.openssl_* modules for certificate generation
  - Consider integrating with ansible-role-certbot for Let's Encrypt certificates

- **Firewall Configuration**: 
  - UFW configuration in security.rb should be migrated to ansible.posix.ufw module
  - Ensure all required ports (22, 80, 443) remain accessible

- **Fail2ban Setup**: 
  - Migrate fail2ban configuration to ansible.builtin.template for configuration files
  - Use ansible.builtin.service to manage the fail2ban service

- **SSH Hardening**:
  - Disable root login and password authentication settings should be migrated using ansible.posix.sshd_config module

- **Vault/secrets management**:
  - Redis password in cache cookbook should be stored in Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook should be stored in Ansible Vault
  - Total credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: The dynamic generation of multiple virtual hosts based on node attributes
  - Solution: Use Ansible loops with templates to generate site configurations from variables

- **Service Orchestration**: 
  - Challenge: Ensuring proper service restart/reload only when needed
  - Solution: Use Ansible handlers and notify mechanism to restart services only when configurations change

- **Database Initialization**: 
  - Challenge: PostgreSQL database and user creation with proper permissions
  - Solution: Use community.postgresql.postgresql_* modules with idempotent operations

- **Redis Configuration Customization**: 
  - Challenge: The Chef cookbook uses a ruby_block to modify Redis configuration
  - Solution: Create a custom Redis configuration template in Ansible with all required settings

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, UFW)
   - Add virtual host configuration

2. **cache** (Priority 2)
   - Memcached and Redis services that may be required by applications
   - Relatively self-contained with few dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on properly configured web server and database
   - More complex with Python environment setup, Git repository management, and database configuration

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS/Fedora)
2. Self-signed certificates are acceptable for development, but production may require proper certificates
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain accessible
4. The security requirements (fail2ban, UFW, SSH hardening) will remain the same
5. The PostgreSQL database will be installed locally on the same server
6. The Redis password and PostgreSQL credentials in the Chef recipes are development credentials and can be replaced
7. The Vagrant development environment will be maintained for testing
8. The multi-site configuration with test.cluster.local, ci.cluster.local, and status.cluster.local will be preserved