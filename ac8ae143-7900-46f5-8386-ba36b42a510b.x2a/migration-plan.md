# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Self-signed SSL certificates management

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening with fail2ban and UFW

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbook structure
- `solo.rb`: Chef Solo configuration - will be replaced by Ansible configuration
- `solo.json`: Node attributes and run list - will be replaced by Ansible inventory and variables
- `Vagrantfile`: Development environment definition - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package management
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks or community roles

### Security Considerations

- **SSL/TLS Management**: Self-signed certificates are generated for development; migration should maintain this capability while allowing for production certificates
- **Firewall (UFW)**: Security hardening with UFW needs to be migrated to equivalent Ansible firewall management
- **fail2ban**: Intrusion prevention configuration needs to be migrated
- **SSH Hardening**: SSH security configurations (disable root login, password authentication) need to be preserved
- **Redis Authentication**: Password authentication for Redis must be maintained
- **PostgreSQL Security**: Database user creation with password needs secure handling
- **Secrets Management**: Passwords in plaintext (Redis, PostgreSQL) should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of site configurations based on attributes needs careful translation to Ansible templates and variables
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated in Ansible
- **Service Dependencies**: Ensuring proper ordering of service installation and configuration (e.g., PostgreSQL before FastAPI application)
- **Idempotency**: Ensuring all operations remain idempotent, particularly database user creation and certificate generation

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Base Nginx installation and configuration
   - SSL certificate management
   - Virtual host configuration
   - Security hardening (fail2ban, UFW)

2. **cache** (low complexity, independent service)
   - Memcached configuration
   - Redis installation and security setup

3. **fastapi-tutorial** (high complexity, depends on database)
   - PostgreSQL installation and configuration
   - Database and user creation
   - Python environment setup
   - Application deployment
   - Systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions (Ubuntu 18.04+, CentOS 7+)
2. Self-signed certificates are acceptable for development environments
3. The same security practices (fail2ban, UFW, SSH hardening) are desired in the Ansible implementation
4. The FastAPI application source will continue to be available at the specified Git repository
5. The current directory structure and naming conventions can be adapted to Ansible best practices
6. Redis and PostgreSQL passwords will be managed securely through Ansible Vault
7. The Vagrant development environment will be maintained but adapted for Ansible provisioning