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
- Self-contained environment with Vagrant for testing

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbook structure
- `solo.rb`: Chef Solo configuration - will be replaced by Ansible configuration
- `solo.json`: Node attributes and run list - will be replaced by Ansible inventory and variables
- `Vagrantfile`: Development environment definition - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migrate to Ansible's crypto modules for certificate generation or consider integrating with Let's Encrypt.
- **Firewall Configuration (UFW)**: Migrate UFW rules to Ansible's ufw module or firewalld for Fedora/RHEL systems.
- **fail2ban Configuration**: Migrate fail2ban configuration to Ansible's template module.
- **SSH Hardening**: Preserve SSH security configurations (disable root login, password authentication).
- **Redis Authentication**: Ensure Redis password is stored securely using Ansible Vault.
- **PostgreSQL Authentication**: Secure database credentials using Ansible Vault.
- **System Hardening**: Migrate sysctl security configurations.

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of site configurations based on node attributes will need to be replicated using Ansible's template system and variables.
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be carefully migrated to maintain security.
- **Service Dependencies**: Ensure proper ordering of service installations and configurations, particularly for the FastAPI application which depends on PostgreSQL.
- **Platform Compatibility**: The current setup supports both Debian/Ubuntu and RHEL/CentOS families. Ansible playbooks should maintain this compatibility.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add site configuration templates
   - Add security hardening (fail2ban, UFW)

2. **cache** (Priority 2)
   - Independent service that can be migrated after core infrastructure
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on database
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment and service configuration

### Assumptions

1. The migration will maintain the same target operating systems (Ubuntu 18.04+, CentOS 7+, Fedora 42).
2. Self-signed certificates are acceptable for the migrated solution (production environments might require proper certificates).
3. The FastAPI application source code will remain at the same GitHub repository.
4. The current security configurations are appropriate and should be maintained.
5. The Vagrant development environment will be preserved for testing the Ansible playbooks.
6. Redis and PostgreSQL passwords in the Chef recipes should be replaced with Ansible Vault secured variables.
7. The directory structure for web content (/var/www/[site]) will be maintained.
8. The current Chef attributes will be mapped to Ansible variables with similar structure.