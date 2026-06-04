# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations that need careful migration
- External dependencies on community cookbooks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

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
- `solo.json`: Chef node configuration with run list and attributes - will be replaced by Ansible inventory and variables
- `solo.rb`: Chef configuration file - will be replaced by Ansible configuration
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM - will be replaced by Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's ufw module or firewalld for Fedora/RHEL systems

- **Fail2ban Configuration**: 
  - Configured for SSH and potentially other services
  - Migration approach: Use Ansible's template module with fail2ban configuration templates

- **SSH Hardening**: 
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's lineinfile or template module for sshd_config

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (redis_secure_password_123)
  - PostgreSQL password is hardcoded in the recipe (fastapi_password)
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically creates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible's template module with Jinja2 templates to achieve similar functionality

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt

- **Database User and Schema Creation**: 
  - Description: PostgreSQL user and database creation is handled via shell commands
  - Mitigation: Use Ansible's postgresql_* modules for more idempotent database management

- **Service Orchestration**: 
  - Description: Services have dependencies (e.g., FastAPI depends on PostgreSQL)
  - Mitigation: Use Ansible's handlers and meta dependencies to ensure proper service ordering

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, ufw, sysctl)
   - Add multi-site configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for development/testing, but production may require proper certificates.
3. The security requirements (fail2ban, firewall, SSH hardening) will remain the same.
4. The FastAPI application repository will remain available at the specified URL.
5. The current Redis and PostgreSQL passwords are development passwords and will be replaced with proper secrets management.
6. The current directory structure in the target environment (/opt/fastapi-tutorial, /var/www/sites) will be maintained.
7. The Nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same.
8. The current port mappings and network configuration will be maintained.