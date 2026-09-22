# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating security configurations including firewall rules, fail2ban, and SSL certificate management.

**Estimated Timeline**: 4-6 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security hardening
**Team Coordination**: Requires coordination between application, infrastructure, and security teams

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
    - Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, self-signed certificate generation, UFW firewall rules, fail2ban jail configuration, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes - contains site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or direct package installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and ansible.builtin.template for configuration

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to ansible.builtin.openssl_* modules
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **SSH Hardening**: Root login disable, password authentication disable - migrate to ansible.builtin.lineinfile for sshd_config
- **Fail2ban Integration**: Custom jail configuration - migrate to community.general.fail2ban module
- **Vault/secrets management**: 
  - Redis password hardcoded in recipe (redis_secure_password_123)
  - PostgreSQL password hardcoded in recipe (fastapi_password)
  - Database credentials in .env file
  - SSL certificate generation without external CA integration
  - Recommend migrating to Ansible Vault for credential management

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - will need to be replaced with ansible.builtin.replace or ansible.builtin.lineinfile tasks
- **Dynamic Site Generation**: The nginx-multisite cookbook dynamically creates sites based on node attributes - will require Ansible loops and template generation
- **Service Dependencies**: PostgreSQL must be running before database user creation - requires proper task ordering and handlers
- **File Permissions**: Complex SSL certificate permissions (ssl-cert group) - ensure proper group management in Ansible

### Migration Order

1. **cache** (low risk, standalone service)
2. **fastapi-tutorial** (moderate complexity, database dependencies)
3. **nginx-multisite** (high complexity, security configurations, SSL management)

### Assumptions

- Current Chef cookbooks are working in production environment
- External cookbook dependencies (nginx, memcached, redisio) are stable and their functionality can be replicated with Ansible modules
- Self-signed certificates are acceptable for the target environment (no external CA integration required)
- PostgreSQL installation and configuration outside of user/database creation is handled elsewhere
- The ruby_block configuration fixes in the cache cookbook are still necessary for Redis functionality
- UFW is the preferred firewall solution (not iptables or firewalld)
- Systemd is available on target systems for service management
- Git repository access for FastAPI tutorial code will remain available during migration
- Current hardcoded passwords are acceptable for development but should be moved to Ansible Vault for production