# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks to Ansible roles, addressing external dependencies, and ensuring security configurations are properly maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:**
- Medium complexity due to multiple interconnected services
- Security configurations require careful attention
- External dependencies on Redis and Memcached need proper handling

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
  - Migration consideration: Replace with Ansible Galaxy requirements.yml
  
- `solo.json`: Chef node configuration with run list and attribute overrides
  - Migration consideration: Convert to Ansible group_vars or host_vars

- `solo.rb`: Chef configuration file for Chef Solo
  - Migration consideration: Replace with ansible.cfg

- `Vagrantfile`: Defines development VM using Fedora 42
  - Migration consideration: Update for Ansible provisioning instead of Chef

- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
  - Migration consideration: Replace with Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Current approach uses self-signed certificates generated with OpenSSL
  - Migration approach: Use Ansible crypto modules for certificate generation or integrate with Let's Encrypt

- **Firewall Configuration**: 
  - Current approach uses UFW with specific rules
  - Migration approach: Use Ansible UFW module or firewalld module depending on target OS

- **Fail2ban Configuration**: 
  - Current approach installs and configures fail2ban
  - Migration approach: Use Ansible to install and configure fail2ban

- **SSH Hardening**: 
  - Current approach disables root login and password authentication
  - Migration approach: Use Ansible to configure SSH or leverage ansible.posix.ssh_config module

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe ('redis_secure_password_123')
  - PostgreSQL password is hardcoded in the recipe ('fastapi_password')
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of multiple virtual hosts
  - Mitigation: Use Ansible templates with loops to generate site configurations

- **SSL Certificate Generation**: 
  - Challenge: Ensuring certificates are only generated when needed
  - Mitigation: Use Ansible's idempotent modules and conditionals to check for existing certificates

- **Service Dependencies**: 
  - Challenge: Ensuring proper ordering of service installation and configuration
  - Mitigation: Use Ansible handlers and proper task dependencies

- **Database Initialization**: 
  - Challenge: Creating PostgreSQL users and databases idempotently
  - Mitigation: Use Ansible's postgresql_* modules with proper conditionals

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, UFW)
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Deploy FastAPI application from Git
   - Configure Python environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for development; production may require integration with a certificate authority.
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and Memcached configurations meet performance requirements.
6. The PostgreSQL database setup is sufficient for the FastAPI application's needs.
7. The current directory structure in /opt and /var will be maintained in the target environment.
8. The systemd service configuration for FastAPI is appropriate and doesn't require changes.
9. The Nginx virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same.
10. The current user permissions and ownership settings are appropriate for the target environment.