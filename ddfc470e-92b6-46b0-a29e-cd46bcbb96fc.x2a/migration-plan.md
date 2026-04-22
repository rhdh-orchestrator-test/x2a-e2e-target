# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Some security configurations that need careful migration
- Moderate number of templates and configuration files

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall setup
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the Chef run list and configuration attributes for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding and networking configuration

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module and custom templates
- **memcached (~> 6.0)**: Replace with Ansible's `community.general.memcached` module
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Chef generates self-signed certificates for development
  - Migration approach: Use Ansible's `community.crypto.openssl_*` modules for certificate generation

- **Firewall Configuration**: 
  - Chef configures UFW with specific rules
  - Migration approach: Use Ansible's `community.general.ufw` module

- **Fail2ban Setup**: 
  - Chef installs and configures fail2ban
  - Migration approach: Use Ansible's `community.general.fail2ban` module

- **SSH Hardening**: 
  - Chef disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or `ansible.posix.sshd` module

- **Vault/secrets management**:
  - Redis password in plaintext in the cache cookbook
  - PostgreSQL credentials in plaintext in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Replicating the dynamic site configuration from Chef
  - Mitigation: Create Ansible templates with Jinja2 loops to generate site configurations

- **SSL Certificate Generation**: 
  - Challenge: Ensuring proper permissions and security for SSL certificates
  - Mitigation: Use Ansible's file permissions and owner/group settings carefully

- **Service Dependencies**: 
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and `notify` directives to manage service dependencies

- **Redis Configuration Hack**: 
  - Challenge: The Chef cookbook uses a ruby_block to modify Redis configuration
  - Mitigation: Create a proper Ansible template for Redis configuration instead of modifying files after creation

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create Ansible role for Nginx installation and configuration
   - Create templates for site configuration
   - Implement security configurations (fail2ban, ufw)

2. **cache** (low complexity, independent service)
   - Create Ansible roles for Memcached and Redis
   - Implement Redis authentication using Ansible Vault for password storage

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Create Ansible role for PostgreSQL setup
   - Create role for FastAPI application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The same security hardening measures should be applied in the Ansible solution
4. The FastAPI application source will continue to be pulled from the same Git repository
5. Redis and Memcached configurations should match the current setup
6. The Nginx multi-site configuration pattern should be preserved
7. No additional monitoring or logging solutions are required beyond what's in the current setup
8. The migration will not involve containerization of the services
9. The current directory structure and naming conventions for web content will be maintained
10. The PostgreSQL database schema will be created by the FastAPI application itself