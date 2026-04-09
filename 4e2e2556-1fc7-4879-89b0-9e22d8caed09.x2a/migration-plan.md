# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- Security configurations are comprehensive and will require careful migration
- External dependencies on community cookbooks will need Ansible Galaxy equivalents

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git-based deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy file defining the run list and cookbook versions - will be replaced by Ansible playbook structure
- `solo.rb`: Chef Solo configuration - will be replaced by Ansible configuration
- `solo.json`: Node attributes and run list - will be replaced by Ansible inventory and variables
- `Vagrantfile`: Development environment configuration - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for integration with Let's Encrypt or other certificate authorities.
- **Firewall Configuration**: UFW configuration should be migrated to equivalent Ansible UFW module tasks.
- **Fail2ban Setup**: Fail2ban configuration should be preserved in the Ansible migration.
- **SSH Hardening**: SSH security settings (disabling root login, password authentication) should be maintained.
- **Redis Authentication**: Redis password authentication must be preserved with secure password handling.
- **PostgreSQL Authentication**: Database credentials for FastAPI application should be securely managed.

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes will need to be implemented using Ansible templates and variables.
- **SSL Certificate Generation**: Self-signed certificate generation logic will need to be replicated in Ansible.
- **Security Hardening**: Comprehensive security configurations across multiple services will require careful testing.
- **Service Dependencies**: Ensuring proper ordering of service installation, configuration, and startup in Ansible.
- **Password Management**: Secure handling of Redis and PostgreSQL passwords will require Ansible Vault or similar solution.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Create base Nginx role
   - Implement virtual host configuration
   - Migrate SSL certificate generation
   - Implement security hardening (fail2ban, ufw)

2. **cache** (Priority 2): Supporting services
   - Create Memcached role or use Galaxy role
   - Create Redis role with authentication
   - Test integration with Nginx

3. **fastapi-tutorial** (Priority 3): Application layer
   - Create PostgreSQL role
   - Create Python/FastAPI application deployment role
   - Configure systemd service
   - Test integration with all components

### Assumptions

1. The current Chef setup is functional and represents the desired end state.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use proper certificates).
3. The security configurations are appropriate and should be maintained as-is.
4. The Vagrant development environment should be preserved with Ansible provisioning.
5. No changes to the application code or architecture are required during migration.
6. The Redis password and PostgreSQL credentials in the code are development values that will be replaced with secure values in production.
7. The target environment will continue to be Fedora/RHEL-based systems with support for Ubuntu/Debian.