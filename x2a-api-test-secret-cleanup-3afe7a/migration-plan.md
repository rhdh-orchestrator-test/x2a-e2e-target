# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-7 weeks

**Complexity Assessment**: Medium
- The repository has well-structured Chef cookbooks with clear dependencies
- Security configurations are present and need careful migration
- External cookbook dependencies need to be replaced with Ansible Galaxy roles or custom implementations

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on external cookbooks

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file containing the run list and node attributes. Defines Nginx site configurations and security settings.
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines a Fedora 42 VM for local development and testing with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef, install dependencies, and run Chef Solo.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata. The Vagrantfile uses Fedora 42 for development.
- **Virtual Machine Technology**: Vagrant with libvirt provider for local development.
- **Cloud Platform**: Not specified in the repository. The configuration appears to be designed for on-premises or generic cloud VMs.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role (e.g., `geerlingguy.redis`) or custom role

### Security Considerations

- **SSL Certificate Management**: 
  - The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation or integrate with Let's Encrypt using `community.crypto.acme_certificate`

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's `ufw` module or `firewalld` module depending on target OS

- **Fail2ban Configuration**: 
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible Galaxy role (e.g., `geerlingguy.security`) or create custom role

- **SSH Hardening**: 
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or dedicated SSH hardening role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe (`fastapi:fastapi_password`)
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Replicating the dynamic site configuration from Chef to Ansible
  - Mitigation: Create Ansible templates with Jinja2 loops to iterate through site configurations

- **Redis Configuration Hack**: 
  - Challenge: The Chef recipe includes a hack to modify Redis configuration
  - Mitigation: Create proper Redis configuration template in Ansible without relying on post-configuration modifications

- **Service Orchestration**: 
  - Challenge: Ensuring proper service start order and dependencies
  - Mitigation: Use Ansible handlers and meta dependencies to ensure services start in the correct order

- **SSL Certificate Generation**: 
  - Challenge: Replicating the self-signed certificate generation logic
  - Mitigation: Use Ansible's `openssl_*` modules with proper idempotence checks

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Dependent services that the application will use
   - Moderate complexity with external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on both Nginx and database services
   - Contains database setup that should come after infrastructure components

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata.
2. Self-signed certificates are acceptable for the migrated solution, or a proper certificate authority will be specified.
3. The Fedora 42 development environment is not critical and could be replaced with a different OS if needed.
4. The FastAPI application repository at `https://github.com/dibanez/fastapi_tutorial.git` will remain available.
5. The current security settings (disabling root login, password authentication, etc.) should be maintained in the Ansible implementation.
6. The hardcoded credentials in the recipes will be replaced with more secure solutions in the Ansible implementation.
7. The current port mappings and network configurations will be maintained in the Ansible implementation.