# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-7 weeks

**Complexity Assessment:**
- Medium complexity due to multiple services and security configurations
- Moderate dependency on external cookbooks that need Ansible equivalents
- Security configurations that require careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on external cookbooks

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git-based deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket. Migration will require mapping these dependencies to Ansible Galaxy roles or custom implementations.
- `solo.json`: Contains the Chef run list and node attributes. Will need to be converted to Ansible inventory variables or group_vars.
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings. Ansible equivalent would be ansible.cfg.
- `Vagrantfile`: Defines the development VM configuration. Can be reused with minimal changes to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks. Will need to be replaced with Ansible installation and playbook execution.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting local development with Vagrant

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible community.general.memcached module or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible community.redis collection or custom Redis role

### Security Considerations

- **SSL Certificate Management**: 
  - The current implementation generates self-signed certificates
  - Migration approach: Use Ansible crypto modules (openssl_certificate, openssl_privatekey) for certificate generation

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible ufw module to maintain identical firewall rules

- **Fail2ban Configuration**: 
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible to deploy fail2ban with equivalent configuration templates

- **SSH Hardening**: 
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible to configure SSH with identical security settings

- **Vault/secrets management**:
  - Redis password hardcoded in recipe (redis_secure_password_123)
  - PostgreSQL password hardcoded in recipe (fastapi_password)
  - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with similar logic to generate site configurations from variables

- **Redis Configuration Hack**: 
  - Description: The current implementation includes a ruby_block to modify Redis configuration files after they're created
  - Mitigation: Create a custom Redis configuration template in Ansible that correctly formats the configuration initially

- **Service Orchestration**: 
  - Description: The current implementation has specific service restart notifications
  - Mitigation: Use Ansible handlers to maintain the same service restart logic

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Dependent services that the application will need
   - Moderate complexity with external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on both Nginx and PostgreSQL
   - Contains database setup that should come after infrastructure components

### Assumptions

1. The target environment will continue to be Fedora 42 as specified in the Vagrantfile
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The same security hardening approach (fail2ban, UFW, SSH configuration) is desired in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The current Redis and PostgreSQL passwords are development passwords and will be replaced with more secure values in production
6. The Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
7. The current implementation is for development/testing purposes as indicated by the Vagrant setup