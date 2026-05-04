# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 3-4 weeks, with moderate complexity due to the multi-site configuration and security hardening requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the Chef run list and configuration parameters for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration using Fedora 42 with port forwarding and networking

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation or integrate with Let's Encrypt using `geerlingguy.certbot`

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's `ufw` module or `firewalld` module (more appropriate for Fedora)

- **fail2ban Integration**:
  - Current implementation configures fail2ban for intrusion prevention
  - Migration approach: Use Ansible's `template` module to configure fail2ban or use a dedicated role like `geerlingguy.security`

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration approach: Use Ansible Vault to encrypt sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically creates multiple virtual hosts with SSL
  - Mitigation: Create Ansible templates with Jinja2 loops to generate site configurations from variables

- **Service Coordination**: 
  - Description: Interdependencies between services (PostgreSQL, FastAPI, Redis)
  - Mitigation: Use Ansible handlers and proper dependency ordering in playbooks

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's `openssl_*` modules with proper idempotency checks

- **Security Hardening**: 
  - Description: Multiple security layers (fail2ban, UFW, SSH hardening, sysctl settings)
  - Mitigation: Break security configurations into separate tasks with clear documentation

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement virtual hosts configuration
   - Add security hardening features

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy Python application from Git
   - Configure virtual environment and dependencies
   - Create systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (the Vagrantfile specifies Fedora 42)
2. Self-signed certificates are acceptable for the migrated solution (production would likely require proper certificates)
3. The security requirements will remain the same (fail2ban, firewall, SSH hardening)
4. The current directory structure in `/opt/server/` for website content and `/opt/fastapi-tutorial` for the application will be maintained
5. The PostgreSQL database structure and credentials can remain the same
6. Redis authentication will continue to be required
7. The Vagrant development environment will be replaced with an equivalent Ansible-based setup

## Implementation Plan

### Phase 1: Setup and Structure (Week 1)

1. Create Ansible project structure with roles, playbooks, and inventory
2. Set up Ansible Vault for secrets management
3. Create base role for common configurations
4. Develop Vagrant integration for testing

### Phase 2: Core Services Migration (Week 2)

1. Develop Nginx role with multi-site support
2. Implement SSL certificate generation
3. Migrate security hardening configurations
4. Create caching services roles (Redis and Memcached)

### Phase 3: Application Migration (Week 3)

1. Develop PostgreSQL role
2. Create FastAPI application deployment role
3. Implement systemd service configuration
4. Test full stack deployment

### Phase 4: Testing and Documentation (Week 4)

1. Comprehensive testing of all components
2. Documentation of roles, variables, and playbooks
3. Create example inventory and deployment guides
4. Knowledge transfer sessions