# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks to Ansible roles and playbooks, addressing external dependencies, and ensuring security configurations are properly maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear dependencies
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate management, security hardening with fail2ban and UFW

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

- **Operating System**: Supports Ubuntu 18.04+ and CentOS 7+, with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks

### Security Considerations

- **SSL Certificate Management**: Migration must maintain proper certificate generation and permissions
  - Current implementation uses self-signed certificates with proper permissions
  - Ansible equivalent should use the `openssl_*` modules

- **Firewall Configuration (UFW)**: Convert UFW rules to Ansible ufw module
  - Default deny policy
  - Allow SSH, HTTP, HTTPS

- **fail2ban Configuration**: Migrate fail2ban setup to Ansible
  - Custom jail configuration

- **SSH Hardening**: Maintain SSH security settings
  - Disable root login
  - Disable password authentication

- **Redis Authentication**: Ensure Redis password is securely managed
  - Current implementation has hardcoded password in recipe
  - Should use Ansible Vault for password storage

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation dynamically creates site configurations based on node attributes. Ansible equivalent will need to use templates and variable loops.

- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be carefully migrated to maintain security.

- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible handlers and wait_for modules may be needed to ensure proper service startup order.

- **Python Environment Management**: The FastAPI deployment uses Python virtual environments which will need to be managed with Ansible's pip module.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Basic Nginx installation
   - Security configurations
   - SSL certificate management
   - Site configurations

2. **cache** (low complexity, standalone service)
   - Memcached configuration
   - Redis installation and security

3. **fastapi-tutorial** (high complexity, depends on database)
   - PostgreSQL installation and configuration
   - Python environment setup
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to be Linux-based (Ubuntu/CentOS/Fedora)
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security configurations are appropriate for the target environment
5. Redis password and PostgreSQL credentials will need to be managed securely in Ansible Vault
6. The current directory structure in /var/www/ and /opt/ will be maintained
7. The Vagrant development environment will be migrated to use Ansible provisioning