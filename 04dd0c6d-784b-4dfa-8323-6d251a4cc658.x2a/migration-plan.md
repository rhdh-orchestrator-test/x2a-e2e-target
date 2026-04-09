# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- SSL certificate management
- Security hardening configurations
- Database integration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall rules

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
- `Policyfile.rb`: Chef policy file defining the run list - will be replaced by Ansible playbooks
- `solo.rb`: Chef Solo configuration - will be replaced by Ansible configuration
- `solo.json`: Chef node attributes - will be converted to Ansible variables
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management modules (openssl_*)

### Security Considerations

- **SSL Certificate Management**: Migration must preserve self-signed certificate generation for development environments
- **Firewall Rules (UFW)**: Convert UFW rules to Ansible's firewall modules (ufw or firewalld depending on target OS)
- **fail2ban Configuration**: Ensure fail2ban rules are properly migrated using Ansible's template module
- **SSH Hardening**: Preserve SSH security settings (root login disabled, password authentication disabled)
- **System Hardening**: Migrate sysctl security settings to Ansible sysctl module
- **Redis Authentication**: Ensure Redis password is securely managed in Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: Ensure the dynamic generation of multiple Nginx virtual hosts is preserved in Ansible
- **SSL Certificate Generation**: Implement equivalent self-signed certificate generation in Ansible
- **Service Dependencies**: Maintain proper ordering of service installation and configuration
- **Password Management**: Move hardcoded passwords (Redis, PostgreSQL) to Ansible Vault
- **Idempotency**: Ensure database creation and user setup operations are idempotent

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Base Nginx installation and configuration
   - SSL certificate generation
   - Virtual host configuration
   - Security hardening (fail2ban, firewall)

2. **cache** (low complexity, independent service)
   - Memcached installation and configuration
   - Redis installation and configuration

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - PostgreSQL installation and configuration
   - Python environment setup
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based systems, with potential for Ubuntu/Debian support
2. Self-signed certificates are acceptable for development environments
3. The same security hardening requirements will apply in the new environment
4. The FastAPI application repository will remain accessible at the same URL
5. The current password values can be reused (though they should be moved to Ansible Vault)
6. The same virtual host names will be used in the new environment
7. The directory structure for web content will remain the same
8. The PostgreSQL database schema does not require migration, only the database and user creation