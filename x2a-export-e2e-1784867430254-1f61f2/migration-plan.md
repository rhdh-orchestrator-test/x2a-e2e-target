# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- Security configurations are present and need careful migration
- SSL certificate management requires special attention
- Database and application configurations contain credentials that need secure handling

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains the run list and configuration data - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Installs Chef and runs cookbooks - will be replaced by Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules that need to be migrated to Ansible's ufw module
- **Fail2ban Setup**: Configuration needs to be migrated to Ansible's fail2ban module
- **SSH Hardening**: SSH configuration changes (disabling root login, password authentication) need to be migrated
- **Sysctl Security Settings**: System-level security settings need to be preserved
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - SSL certificates and private keys in nginx-multisite cookbook
  - Total credentials detected: 3 (Redis password, PostgreSQL username/password)

### Technical Challenges

- **SSL Certificate Management**: The Chef cookbook generates self-signed certificates for each site. This needs to be replicated in Ansible, potentially using the openssl module.
- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on attributes needs to be replicated using Ansible templates and variables.
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations, particularly for the FastAPI application which depends on PostgreSQL.
- **Idempotency**: Ensuring that the Ansible playbooks are idempotent, particularly for operations like database creation and user setup.

### Migration Order

1. **nginx-multisite** (Priority 1): This provides the base web server configuration and should be migrated first
   - Create Ansible role for Nginx installation and configuration
   - Implement SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (Priority 2): This provides caching services that may be used by the application
   - Create Ansible roles for Memcached and Redis
   - Configure authentication and security settings
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3): This depends on the web server and potentially the caching services
   - Create Ansible role for Python application deployment
   - Implement PostgreSQL database setup
   - Configure systemd service
   - Set up environment variables and application configuration

### Assumptions

1. The target environment will continue to be Fedora 42 as specified in the Vagrantfile
2. The same directory structure for web content will be maintained
3. Self-signed certificates are acceptable for the migrated solution
4. The same security hardening measures are required in the Ansible implementation
5. The FastAPI application source will continue to be pulled from the same Git repository
6. The PostgreSQL database schema and user permissions will remain the same
7. The Redis and Memcached configurations will maintain the same performance characteristics
8. The Vagrant development environment will be preserved but modified to use Ansible provisioning