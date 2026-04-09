# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, their dependencies, and security configurations to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Core Infrastructure Migration: 2 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5 weeks

**Complexity Assessment**: Medium
- Multiple interconnected services
- SSL certificate management
- Security hardening configurations
- Database integration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
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
    - Key Features: Git-based deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbook structure
- `solo.json`: Chef node configuration - will be migrated to Ansible inventory variables
- `solo.rb`: Chef configuration - will be replaced by Ansible configuration
- `Vagrantfile`: Development environment definition - can be adapted for Ansible with minimal changes
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook calls

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management modules (openssl_*)

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's `openssl_certificate`, `openssl_csr`, and `openssl_privatekey` modules
  - Consider integration with Let's Encrypt using `community.crypto.acme_certificate`

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `ufw` module to manage firewall rules
  - Ensure all existing rules are preserved during migration

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible to manage fail2ban configuration files and service
  - Preserve existing jail configurations

- **SSH Hardening**:
  - Migration approach: Use Ansible's `lineinfile` or templates to configure SSH security settings
  - Consider using `devsec.hardening.ssh_hardening` role

- **Redis Authentication**:
  - Migration approach: Use Ansible Vault to store Redis password
  - Configure Redis using templates with password from vault

### Technical Challenges

- **Multi-site Nginx Configuration**:
  - Description: The current setup dynamically generates Nginx site configurations for multiple domains
  - Mitigation: Create Ansible templates for Nginx site configurations and use loops to generate configs for each site

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for development
  - Mitigation: Use Ansible's openssl modules to generate certificates or integrate with Let's Encrypt

- **Database Integration**:
  - Description: PostgreSQL setup with user and database creation
  - Mitigation: Use Ansible's PostgreSQL modules for database management

- **Service Orchestration**:
  - Description: Coordinating the deployment and configuration of multiple interdependent services
  - Mitigation: Use Ansible handlers and proper task ordering to ensure services are configured and restarted in the correct order

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Base Nginx installation and configuration
   - SSL certificate management
   - Virtual host configuration
   - Security hardening (fail2ban, ufw)

2. **cache** (low complexity, independent service)
   - Memcached configuration
   - Redis installation and security configuration

3. **fastapi-tutorial** (high complexity, depends on database)
   - PostgreSQL installation and configuration
   - Python environment setup
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. Self-signed certificates are acceptable for development, but production may require integration with a certificate authority
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The Redis password "redis_secure_password_123" will need to be stored securely in Ansible Vault
6. The PostgreSQL credentials (user: fastapi, password: fastapi_password) will need to be stored securely in Ansible Vault
7. The current Vagrant development environment will be maintained with Ansible provisioning
8. No changes to the application architecture or deployment strategy are required