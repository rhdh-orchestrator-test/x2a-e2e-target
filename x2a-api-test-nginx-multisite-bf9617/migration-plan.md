# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating security configurations including fail2ban, UFW firewall, and SSL certificate management.

**Estimated Timeline**: 4-6 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security hardening
**Team Coordination**: Requires coordination between web operations, application deployment, and security teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban and UFW, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and node configuration
- `Vagrantfile`: Development environment provisioning - will need Ansible equivalent for local testing
- `vagrant-provision.sh`: Shell provisioning script - may contain additional setup steps to migrate

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or direct package installation and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration templates

### Security Considerations

- **SSH Hardening**: Migration of SSH configuration changes (PermitRootLogin no, PasswordAuthentication no) to Ansible lineinfile or template modules
- **Firewall Management**: UFW commands need conversion to community.general.ufw Ansible module
- **Fail2ban Configuration**: Template-based jail.local configuration needs migration to Ansible template module
- **SSL Certificate Management**: Self-signed certificate generation via OpenSSL commands needs conversion to community.crypto.openssl_* modules
- **Credential Management**: 
  - Redis password (redis_secure_password_123) hardcoded in cache cookbook - needs Ansible Vault
  - PostgreSQL credentials (fastapi:fastapi_password) hardcoded in fastapi-tutorial cookbook - needs Ansible Vault
  - Database connection strings in .env file contain plaintext passwords - needs Ansible Vault

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex regex-based configuration file manipulation - this will need conversion to Ansible lineinfile or replace modules with multiple tasks
- **Service Dependencies**: PostgreSQL service must be running before database user creation in fastapi-tutorial - requires proper Ansible task ordering and handlers
- **SSL Certificate Generation**: Self-signed certificate creation with specific ownership and permissions needs careful conversion to Ansible crypto modules
- **Multi-site Configuration**: Dynamic site creation based on node attributes requires Ansible loops and template generation

### Migration Order

1. **cache** (low risk, standalone service) - Start with caching services as they have minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Core web infrastructure with security hardening, foundational for other services  
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, should be migrated after web infrastructure is stable

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require CA-signed certificates)
- The ruby_block configuration fixes in the Redis setup are still necessary in the target environment
- PostgreSQL will be installed locally rather than using an external database service
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible during migration
- Current hardcoded passwords are acceptable for development but will need proper secret management in production
- UFW firewall rules and fail2ban configuration requirements remain the same in the target environment
- The systemd service configuration approach for FastAPI application is appropriate for the target environment