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
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations and SSL certificate management require careful handling
- Secrets management needs to be implemented with Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW firewall

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on community cookbooks

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external dependencies with version constraints. Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Chef configuration file containing the run list and node attributes. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM configuration using Vagrant. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Shell script to install Chef and run the provisioning process. Will be replaced by Ansible provisioning commands.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's built-in `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role such as `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role such as `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's `ufw` module to maintain the same security posture.
- **fail2ban Setup**: The Chef cookbook configures fail2ban. Migration should use Ansible's `fail2ban` module or a community role.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Migration should use Ansible's `lineinfile` module or the `ansible-hardening` role.
- **SSL Certificate Management**: The Chef cookbook generates self-signed certificates. Migration should use Ansible's `openssl_*` modules.
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - These should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on node attributes. This pattern needs to be replicated in Ansible using loops and templates.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates. This needs to be handled carefully in Ansible to ensure certificates are only generated when needed.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible handlers and conditional checks will be needed to ensure proper service ordering.
- **Redis Configuration**: The Chef cookbook includes a hack to fix Redis configuration. This may need special handling in Ansible.

### Migration Order

1. **nginx-multisite** (Priority 1): This is the foundation for the web infrastructure and should be migrated first.
2. **cache** (Priority 2): The caching services should be migrated next as they are relatively self-contained.
3. **fastapi-tutorial** (Priority 3): The application deployment should be migrated last as it depends on the web server and database.

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as specified in the Vagrantfile).
2. The current self-signed SSL certificate approach is acceptable for the migrated solution.
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution.
4. The FastAPI application source will continue to be pulled from the GitHub repository specified in the cookbook.
5. The current Redis and Memcached configurations are sufficient for the application needs.
6. The PostgreSQL database schema is managed by the FastAPI application and does not require additional migration steps.
7. The current directory structure for web content and application files will be maintained.
8. The current systemd service configuration for the FastAPI application will be maintained.