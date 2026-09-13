# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating security configurations including fail2ban, UFW firewall, and SSL certificate management.

**Estimated Timeline**: 4-6 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security hardening
**Team Coordination**: Single team can handle migration with Chef and Ansible expertise

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation via external cookbook, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo node configuration with run list and attribute overrides for site configurations and security settings
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning - will need Ansible equivalent for local testing
- `vagrant-provision.sh`: Shell provisioning script - may contain additional setup steps to migrate

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be generic Linux deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules for memcached installation and management
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, ansible.builtin.template for redis.conf, and ansible.builtin.service modules

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to ansible.builtin.openssl_* modules or community.crypto collection
- **Hardcoded Credentials**: 
  - Redis password ('redis_secure_password_123') in cache cookbook - move to Ansible Vault
  - PostgreSQL credentials ('fastapi_password') in fastapi-tutorial cookbook - move to Ansible Vault
  - Database connection strings in .env file - secure with Ansible Vault
- **SSH Hardening**: Root login disable and password authentication disable - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban Configuration**: Jail configuration template - migrate to ansible.builtin.template with fail2ban service management
- **Sysctl Security Tuning**: Security kernel parameters - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook contains a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be replaced with proper Ansible template management or lineinfile modules
- **Multi-site SSL Certificate Generation**: Each site requires individual SSL certificate generation with specific subject parameters - will need Ansible loops with community.crypto.x509_certificate module
- **Service Dependencies**: FastAPI service depends on PostgreSQL being available - ensure proper Ansible task ordering and handlers
- **File Permissions**: SSL private keys require specific group ownership (ssl-cert) - ensure proper Ansible file module usage with group management

### Migration Order

1. **cache** (low risk, straightforward service installation)
2. **nginx-multisite** (moderate complexity, security configurations but well-defined)
3. **fastapi-tutorial** (highest complexity, application deployment with database dependencies)

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require proper CA-signed certificates)
- The current hardcoded passwords are acceptable to migrate to Ansible Vault (may need password rotation)
- The Ruby-based Redis configuration patching indicates potential issues with the redisio cookbook that may not exist with direct Ansible redis configuration
- The Vagrant development environment will be replaced with an equivalent Ansible-based local testing setup
- The solo.json attribute overrides represent the desired production configuration values
- PostgreSQL database initialization commands using sudo -u postgres are acceptable in the target environment
- The systemd service configuration for FastAPI is appropriate for the target deployment environment