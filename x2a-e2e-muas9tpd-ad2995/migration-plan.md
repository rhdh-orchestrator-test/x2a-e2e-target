# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating security configurations including firewall rules, fail2ban, and SSL certificate management.

**Estimated Timeline**: 4-6 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security hardening
**Team Coordination**: Requires coordination between web application, database, and security teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment setup, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with node attributes for site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and node configuration
- `Vagrantfile`: Development environment provisioning - will need equivalent Ansible testing setup
- `vagrant-provision.sh`: Shell provisioning script - functionality should be incorporated into Ansible playbooks

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or direct package installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and ansible.builtin.template for configuration

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation via OpenSSL commands - migrate to ansible.builtin.openssl_* modules or community.crypto collection
- **Firewall Configuration**: UFW firewall rules configured via shell commands - migrate to community.general.ufw module
- **SSH Hardening**: Direct SSH configuration file modification - migrate to ansible.builtin.lineinfile module with proper validation
- **Fail2ban Configuration**: Template-based jail configuration - migrate to ansible.builtin.template with fail2ban service management
- **Sysctl Security Tuning**: Security kernel parameters via template - migrate to ansible.posix.sysctl module

### Vault/secrets management

- **cache module**: Contains hardcoded Redis password ('redis_secure_password_123') in recipe file - requires Ansible Vault encryption
- **fastapi-tutorial module**: Contains hardcoded PostgreSQL password ('fastapi_password') in recipe and .env file - requires Ansible Vault encryption
- **nginx-multisite module**: SSL certificate generation with embedded certificate details - consider parameterizing certificate subject information

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - will need to be replaced with ansible.builtin.replace or ansible.builtin.lineinfile tasks with multiple regex patterns
- **Dynamic Site Configuration**: The nginx-multisite cookbook dynamically creates sites based on node attributes - will require Ansible loops and conditional logic using with_dict or with_items
- **Service Dependencies**: PostgreSQL service must be running before database creation in fastapi-tutorial - requires proper task ordering and service state verification
- **File Permissions**: Complex SSL certificate file permissions (ssl-cert group, 640/710 modes) - ensure proper ansible.builtin.file module usage with group management

### Migration Order

1. **cache** (low risk, standalone service) - Start with caching services as they have minimal dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies
3. **nginx-multisite** (high complexity) - Complex multi-site configuration with security hardening dependencies

### Assumptions

- Target systems will have the same OS support (Ubuntu 18.04+, CentOS 7+) as defined in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require CA-signed certificates)
- The ruby_block configuration fixes in the Redis cookbook are still necessary in the target environment
- UFW firewall is the preferred firewall solution (may need to adapt for RHEL/CentOS systems using firewalld)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible during migration
- Current hardcoded passwords are acceptable for development but will need proper secret management for production
- Systemd is available on target systems for service management (true for supported OS versions)
- The ssl-cert group exists or can be created on target systems for SSL certificate management