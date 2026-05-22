# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations are present and need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef run list and node attributes configuration
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for local development/testing environment

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role such as `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role such as `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's `openssl_*` modules to generate certificates
  - Ensure proper permissions on private keys (640, root:ssl-cert)

- **Firewall Configuration**:
  - UFW is configured with default deny and specific allow rules
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules

- **Fail2ban Configuration**:
  - Fail2ban is installed and configured for brute force protection
  - Migration approach: Use Ansible Galaxy role for fail2ban or create custom role

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's `lineinfile` module or dedicated SSH hardening role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of site configurations
  - Mitigation: Use Ansible templates with loops to generate site configurations

- **SSL Certificate Management**:
  - Challenge: Ensuring proper certificate generation and permissions
  - Mitigation: Use Ansible's `openssl_*` modules and file permissions management

- **Service Dependencies**:
  - Challenge: Ensuring proper service startup order (e.g., PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and service dependencies in systemd unit files

- **Redis Configuration Hack**:
  - Challenge: The Chef recipe includes a hack to modify Redis configuration
  - Mitigation: Create a proper Redis configuration template in Ansible

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security configurations (fail2ban, ufw)
   - Add virtual host configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
3. The same security hardening measures should be applied in the Ansible solution.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current network configuration (ports, IP addresses) should be maintained.
6. The Vagrant development environment should be preserved but converted to use Ansible provisioning.
7. No additional monitoring or logging solutions are required beyond what's in the current Chef implementation.