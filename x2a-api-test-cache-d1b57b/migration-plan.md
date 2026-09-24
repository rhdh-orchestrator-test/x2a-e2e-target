# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv setup, PostgreSQL database/user creation, systemd service management, environment file configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: 
  - Redis password (`redis_secure_password_123`) in cache cookbook
  - PostgreSQL credentials (`fastapi_password`) in fastapi-tutorial cookbook
  - Database connection strings in environment files
- **SSL Certificate Management**: Self-signed certificate generation for development environments needs migration to ansible.builtin.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable configurations
- **Firewall Rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS)
- **Fail2ban Integration**: Jail configuration for nginx protection
- **Sysctl Security**: Kernel parameter tuning for security hardening

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - this will need to be reimplemented using Ansible's lineinfile or replace modules
- **Service Dependencies**: Complex service startup ordering between PostgreSQL, Redis, and application services requires careful Ansible handler and dependency management
- **Multi-site SSL**: Dynamic SSL certificate generation and nginx site configuration based on node attributes needs conversion to Ansible loops and templates
- **Git Repository Management**: FastAPI application deployment via git clone with dependency installation requires Ansible git module and pip module coordination
- **Systemd Service Creation**: Custom systemd service file generation and management needs migration to ansible.builtin.systemd module

### Migration Order

1. **cache** (moderate complexity, foundational service)
2. **nginx-multisite** (high complexity due to SSL and security features, but independent)
3. **fastapi-tutorial** (moderate complexity, depends on database setup)

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- Current hardcoded passwords are development-only and will be replaced with Ansible Vault in production
- PostgreSQL and Redis services can be managed via standard package managers on target systems
- UFW firewall is the preferred firewall solution (may need adaptation for RHEL-based systems using firewalld)
- Systemd is available on all target systems for service management
- Git repository access for FastAPI tutorial application will remain available during migration
- Current Chef Solo deployment model will be replaced with Ansible playbook execution
- Vagrant development environment setup will be maintained or replaced with equivalent Ansible-based provisioning