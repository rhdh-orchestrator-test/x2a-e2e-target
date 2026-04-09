# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Core Infrastructure Migration: 2 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5 weeks

**Complexity Assessment**: Medium
- Multiple interconnected services
- Security configurations that need careful migration
- Database and application deployment requirements

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
- `Policyfile.rb`: Chef policy configuration - will be replaced by Ansible playbook structure
- `solo.json`: Chef node configuration - will be migrated to Ansible inventory variables
- `solo.rb`: Chef configuration - will be replaced by Ansible configuration
- `Vagrantfile`: Development environment configuration - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook calls

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **ssl_certificate (~> 2.1)**: Replace with Ansible crypto modules (openssl_*)
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package configuration

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migrate to Ansible's `openssl_certificate` module with option to use Let's Encrypt.
- **Firewall Configuration (UFW)**: Migrate to Ansible's `ufw` module or `firewalld` module depending on target OS.
- **Fail2ban Configuration**: Migrate to Ansible's template module for fail2ban configuration.
- **SSH Hardening**: Migrate SSH security configurations using Ansible's `lineinfile` or template modules.
- **Redis Authentication**: Ensure Redis password is stored securely using Ansible Vault.
- **PostgreSQL Credentials**: Store database credentials in Ansible Vault.

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts will require careful templating in Ansible.
  - Mitigation: Use Ansible's with_items/loop constructs with templates to generate site configurations.
  
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be preserved.
  - Mitigation: Use Ansible's openssl_* modules to replicate the certificate generation process.

- **Service Orchestration**: Ensuring services start in the correct order with proper dependencies.
  - Mitigation: Use Ansible's handlers and meta dependencies to manage service ordering.

- **Database Initialization**: PostgreSQL database and user creation needs to be idempotent.
  - Mitigation: Use Ansible's postgresql_* modules instead of raw SQL commands.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Then add SSL and security features
   - Finally, implement multi-site configuration

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper integration with Nginx

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service
   - Integrate with Nginx and caching services

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based or Ubuntu/Debian-based systems.
2. Self-signed certificates are acceptable for development; production may require proper CA-signed certificates.
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The Redis password and PostgreSQL credentials will need to be stored securely in the new Ansible setup.
6. The current Vagrant development workflow should be preserved in the Ansible migration.
7. No custom Chef resources are being used that would require special handling in Ansible.
8. The current directory structure in the target environment (/opt/server/*, /var/www/*) should be maintained.