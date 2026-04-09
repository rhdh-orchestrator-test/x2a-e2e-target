# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- **Total: 7 weeks**

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
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `solo.json`: Chef node attributes - will be converted to Ansible variables
- `solo.rb`: Chef configuration - will be replaced by Ansible configuration
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata files. The Vagrantfile uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile.
- **Cloud Platform**: Not specified in the repository. The configuration appears to be designed for on-premises or generic cloud VMs.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management modules (openssl_*)

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migrate to Ansible's `openssl_certificate` module with option to use Let's Encrypt via `community.crypto.acme_certificate`.
- **Firewall Configuration**: UFW configuration should be migrated to Ansible's `ufw` module or `firewalld` module depending on target OS.
- **fail2ban Configuration**: Migrate to Ansible's `template` module for fail2ban configuration.
- **SSH Hardening**: Migrate SSH security configurations using Ansible's `lineinfile` or `template` modules.
- **Redis Authentication**: Ensure Redis password is stored securely using Ansible Vault.

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx sites will require careful templating in Ansible.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated or improved in Ansible.
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI application).
- **Python Environment Management**: Replicating the Python virtual environment setup and dependency installation in Ansible.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Begin with basic Nginx installation
   - Add SSL certificate generation
   - Implement security hardening
   - Configure multi-site setup

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Configure Python environment
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to support the same operating systems (Ubuntu 18.04+ or CentOS 7+).
2. Self-signed certificates are acceptable for development; production may require integration with Let's Encrypt or other certificate authorities.
3. The Redis password "redis_secure_password_123" in the cache cookbook should be replaced with a secure password stored in Ansible Vault.
4. The PostgreSQL password "fastapi_password" in the fastapi-tutorial cookbook should be replaced with a secure password stored in Ansible Vault.
5. The Git repository URL for the FastAPI application (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible.
6. The Vagrant setup is primarily for development/testing and may not reflect the production deployment environment.
7. The current Chef implementation doesn't include backup strategies for PostgreSQL or Redis data, which should be considered in the Ansible implementation.
8. The current implementation doesn't specify monitoring solutions, which could be added during the Ansible migration.