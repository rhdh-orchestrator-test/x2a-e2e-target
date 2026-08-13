# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations and SSL certificate management require careful handling
- Secrets management needs to be improved during migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration including run list and attributes for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file defining cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration using Fedora 42 with port forwarding and networking

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or use the `ansible.builtin.package` module with templates
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` role or use the `ansible.builtin.package` module with templates
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` role or use the `ansible.builtin.package` module with templates

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's `openssl_*` modules to generate self-signed certificates
  - Consider integrating with `community.crypto.acme_certificate` for Let's Encrypt support

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `community.general.ufw` module to configure firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible's `community.general.fail2ban` module or template configuration files

- **SSH Hardening**:
  - Migration approach: Use Ansible's `ansible.posix.sysctl` and template modules to configure SSH security settings

- **Vault/secrets management**:
  - For each module, identified credential patterns:
    - Redis password hardcoded in the cache cookbook (1 credential)
    - PostgreSQL database credentials hardcoded in the fastapi-tutorial cookbook (2 credentials)
    - Environment variables with sensitive data in .env file (1 credential)
  - Migration approach: Use Ansible Vault to securely store and manage these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of multiple virtual host configurations
  - Mitigation: Use Ansible's template module with Jinja2 templates and dictionary variables similar to the Chef attributes

- **SSL Certificate Management**:
  - Challenge: Ensuring proper permissions and ownership for SSL certificates and private keys
  - Mitigation: Use Ansible's file module with appropriate permissions and the openssl_* modules for certificate generation

- **Service Dependencies**:
  - Challenge: Ensuring proper startup order (PostgreSQL before FastAPI application)
  - Mitigation: Use Ansible's handlers and meta dependencies to manage service startup order

- **Idempotent Database Setup**:
  - Challenge: Creating PostgreSQL users and databases idempotently
  - Mitigation: Use Ansible's postgresql_* modules with appropriate when conditions

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear configuration templates

2. **cache** (Priority 2)
   - Depends on external cookbooks (memcached, redisio)
   - Moderate complexity with authentication configuration

3. **fastapi-tutorial** (Priority 3)
   - Most complex with database setup, application deployment, and service configuration
   - Depends on PostgreSQL being properly configured

### Assumptions

1. The target environment will continue to use Vagrant for local development/testing
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
5. Redis and Memcached configurations don't require advanced tuning beyond what's currently specified
6. The PostgreSQL database schema is managed by the FastAPI application and doesn't require additional migration steps
7. The current hardcoded credentials will be replaced with Ansible Vault variables
8. The Nginx configuration will maintain the same virtual host structure with SSL enabled