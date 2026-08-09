# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository contains well-structured Chef cookbooks with clear responsibilities
- No custom resources or complex Chef-specific patterns are used
- Standard configuration patterns that map well to Ansible modules

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, ufw, sysctl)

- **fastapi-tutorial**:
    - Description: FastAPI Python web application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains Chef run list and configuration attributes - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - no direct Ansible equivalent needed
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible
- `vagrant-provision.sh`: Script to install Chef and run cookbooks - will be replaced by Ansible provisioner

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx module and templates
- **memcached (~> 6.0)**: Replace with Ansible memcached module or role
- **redisio (~> 7.2.4)**: Replace with Ansible redis module or role

### Security Considerations

- **SSL/TLS Management**: 
  - Migration approach: Use Ansible crypto modules for certificate generation
  - Consider integrating with Ansible Vault for private key storage

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible UFW module to configure firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible to deploy fail2ban configuration templates

- **SSH Hardening**:
  - Migration approach: Use Ansible ssh_config module to manage SSH configuration

- **Vault/secrets management**:
  - Credentials detected:
    - Redis password in cache cookbook: "redis_secure_password_123"
    - PostgreSQL user/password in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**:
  - Description: The current implementation uses Chef templates to generate site configurations
  - Mitigation: Create Ansible templates with similar structure, using Ansible's template module

- **Self-signed Certificate Generation**:
  - Description: The current implementation uses inline shell commands to generate certificates
  - Mitigation: Use Ansible's openssl_* modules for certificate management

- **Service Orchestration**:
  - Description: The current implementation has interdependent services (Nginx, PostgreSQL, FastAPI application)
  - Mitigation: Use Ansible handlers and proper dependency management in playbooks

### Migration Order

1. **cache** (Priority 1 - Low complexity)
   - Simple configuration of standard services
   - Few dependencies
   - Good starting point to establish patterns

2. **nginx-multisite** (Priority 2 - Medium complexity)
   - Core infrastructure component
   - Multiple templates and configuration files
   - Security configurations

3. **fastapi-tutorial** (Priority 3 - Medium complexity)
   - Application deployment
   - Database configuration
   - Depends on proper web server setup

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for development/testing
3. The same directory structure for web content will be maintained
4. The same security policies will be applied in the Ansible implementation
5. PostgreSQL and Redis passwords will be managed securely in the new implementation
6. The FastAPI application repository URL will remain accessible
7. The same virtual host names will be used in the new implementation