# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
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
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbooks
- `solo.json`: Chef node configuration - will be replaced by Ansible inventory and variables
- `solo.rb`: Chef configuration - will be replaced by Ansible configuration
- `Vagrantfile`: Development environment definition - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook calls

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **ssl_certificate (~> 2.1)**: Replace with Ansible's openssl modules for certificate generation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the Chef cookbook
  - Migration approach: Use Ansible's `openssl_*` modules to generate certificates or integrate with Let's Encrypt

- **Firewall Configuration (UFW)**:
  - Chef configures UFW with specific rules for SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's `ufw` module to configure identical rules

- **Fail2ban Configuration**:
  - Chef installs and configures fail2ban
  - Migration approach: Use Ansible to install fail2ban and template the configuration files

- **SSH Hardening**:
  - Chef disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or dedicated SSH role to apply the same configurations

- **Redis Authentication**:
  - Chef sets a Redis password
  - Migration approach: Use Ansible to configure Redis with password authentication

- **Database Credentials**:
  - PostgreSQL credentials are hardcoded in Chef recipe
  - Migration approach: Use Ansible Vault to store and manage database credentials securely

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of site configurations
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **SSL Certificate Generation**:
  - Challenge: Ensuring proper permissions and security for SSL certificates
  - Mitigation: Use Ansible's file and openssl modules with appropriate permissions

- **Service Orchestration**:
  - Challenge: Ensuring services start in the correct order with proper dependencies
  - Mitigation: Use Ansible handlers and meta dependencies to control service restart order

- **Database Initialization**:
  - Challenge: One-time database setup without repeated execution
  - Mitigation: Use Ansible's PostgreSQL modules with `when` conditions to check for existing databases

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Base Nginx installation
   - Security configurations (fail2ban, ufw)
   - SSL certificate generation
   - Virtual host configuration

2. **cache** (low complexity, standalone service)
   - Memcached configuration
   - Redis installation and security setup

3. **fastapi-tutorial** (high complexity, depends on other services)
   - PostgreSQL installation and configuration
   - Python environment setup
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. Self-signed certificates are acceptable for development, but production may require integration with a certificate authority
3. The security requirements (fail2ban, ufw, SSH hardening) will remain the same
4. The FastAPI application repository will remain available at the specified URL
5. The current Redis and Memcached configurations meet performance requirements and don't need optimization
6. The PostgreSQL database schema is managed by the application and doesn't require additional migration steps
7. The Vagrant development environment will continue to be used for testing
8. No additional monitoring or logging requirements beyond what's in the current Chef configuration