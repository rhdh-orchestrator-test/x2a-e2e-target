# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations and SSL certificate management require careful handling

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

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

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `solo.json`: Chef node attributes and run list - will be converted to Ansible group_vars/host_vars
- `solo.rb`: Chef configuration - will be replaced by ansible.cfg
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW - migrate to Ansible's `community.general.ufw` module
- **Fail2ban Setup**: Migrate fail2ban configuration to Ansible tasks
- **SSH Hardening**: Migrate SSH security configurations (disable root login, password authentication)
- **SSL Certificate Management**: Migrate self-signed certificate generation to Ansible
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts will need careful translation to Ansible templates
- **SSL Certificate Management**: Self-signed certificate generation and management will need to be handled properly
- **Service Dependencies**: Ensuring proper ordering of service installation and configuration
- **Idempotency**: Ensuring all operations are idempotent, especially database user/schema creation

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - First implement basic Nginx installation and configuration
   - Then implement security hardening features
   - Finally implement SSL and virtual host configuration

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (the Vagrantfile specifies Fedora 42)
2. The same network configuration and port mappings will be maintained
3. Self-signed certificates are acceptable (production environments might require Let's Encrypt or other certificate authorities)
4. The FastAPI application repository will remain available at the specified URL
5. The current security configurations are appropriate for the target environment
6. The Redis and PostgreSQL passwords in the code are development passwords and will be replaced with secure passwords in production
7. The current directory structure for web content and application code will be maintained