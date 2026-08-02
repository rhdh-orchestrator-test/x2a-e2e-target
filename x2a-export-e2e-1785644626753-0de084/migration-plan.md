# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and resources to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No complex custom resources or libraries
- Standard infrastructure components (web server, caching, application deployment)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, including security hardening
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

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

- `Berksfile`: Defines cookbook dependencies including external cookbooks from Chef Supermarket (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Defines the run list and configuration parameters for Chef Solo, including Nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Vagrant VM configuration using Fedora 42 with port forwarding and networking
- `vagrant-provision.sh`: Shell script that installs Chef and runs the Chef Solo provisioner in the Vagrant VM

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting local development/testing environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or custom Ansible role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Chef cookbook generates self-signed certificates
  - Migration approach: Use Ansible `openssl_*` modules or community.crypto collection

- **Firewall Configuration (UFW)**:
  - Chef cookbook configures UFW with specific rules
  - Migration approach: Use Ansible `ufw` module

- **Fail2ban Configuration**:
  - Chef cookbook installs and configures fail2ban
  - Migration approach: Use Ansible `community.general.fail2ban` module

- **SSH Hardening**:
  - Chef cookbook modifies SSH configuration to disable root login and password authentication
  - Migration approach: Use Ansible `lineinfile` module or `template` module with SSH config template

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**:
  - Challenge: Dynamically generating multiple virtual host configurations with SSL
  - Mitigation: Use Ansible loops with templates to generate site configurations

- **Service Dependencies**:
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI application)
  - Mitigation: Use Ansible handlers and `notify` to manage service restarts in the correct order

- **SSL Certificate Generation**:
  - Challenge: Generating self-signed certificates with proper permissions
  - Mitigation: Use Ansible's `openssl_*` modules with appropriate file permissions

- **Python Application Deployment**:
  - Challenge: Managing Python virtual environments and dependencies
  - Mitigation: Use Ansible's `pip` module with virtualenv support

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx configuration, then add SSL and security features

2. **cache** (Priority 2)
   - Independent service with moderate complexity
   - Memcached and Redis configuration with authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on PostgreSQL
   - More complex with database setup, environment configuration, and service management

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential support for Ubuntu and CentOS as indicated in the cookbook metadata.
2. The self-signed SSL certificates approach is acceptable for the migrated solution (rather than Let's Encrypt or other CA-signed certificates).
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate and should be maintained in the Ansible solution.
4. The FastAPI application source code will continue to be pulled from the same Git repository.
5. The Redis and PostgreSQL passwords currently hardcoded in the recipes will be moved to Ansible Vault in the migrated solution.
6. The Vagrant development environment will be maintained, but converted to use Ansible provisioner instead of Chef.
7. No changes to the application architecture or deployed services are required as part of the migration.