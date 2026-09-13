# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW firewall, and SSH configuration lockdown
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test/ci/status subdomains), fail2ban intrusion prevention, UFW firewall rules, SSH hardening (root login disabled, password auth disabled), sysctl security tuning

**cache**:
- Description: Caching services layer providing both Redis and Memcached with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication (requirepass), custom log directory setup, configuration file post-processing via ruby_block, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration specifying cookbook paths and logging
- `Vagrantfile`: Development environment provisioning (requires assessment for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for development setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks
- **Chef Solo**: Replace with ansible-playbook execution model

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords identified requiring Ansible Vault migration:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env files
- **SSL Certificate Management**: SSL certificate paths configured but certificate provisioning method unclear - requires investigation of certificate deployment strategy
- **SSH Hardening**: Root login disabled and password authentication disabled via direct sshd_config modification
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH access with default deny policy
- **Fail2ban Integration**: Intrusion prevention with custom jail configuration

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains complex Ruby code for Redis configuration file post-processing that will require translation to Ansible file manipulation tasks
- **Multi-Site SSL Configuration**: nginx-multisite manages multiple SSL-enabled virtual hosts with template-driven configuration requiring careful Ansible template migration
- **Service Dependencies**: Complex service startup ordering (PostgreSQL before FastAPI, nginx after SSL setup) needs proper Ansible handler and dependency management
- **Git Repository Management**: FastAPI application deployment via git clone with revision tracking requires ansible.builtin.git module configuration
- **Python Virtual Environment**: Complex Python venv setup and pip dependency management needs ansible.builtin.pip module with virtualenv support

### Migration Order

1. **cache** (low risk, foundational service) - Redis and Memcached setup with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server and security hardening, depends on SSL certificate strategy
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- SSL certificates are manually deployed or managed externally (no certificate generation/renewal logic found in cookbooks)
- Development environment uses Vagrant but production deployment method is unspecified
- Database initialization scripts and schema management are handled by the FastAPI application itself
- Log rotation and backup strategies are managed outside of these cookbooks
- Network configuration and DNS resolution for *.cluster.local domains are handled externally
- The ruby_block configuration fixes in the cache cookbook address specific Redis version compatibility issues that may not apply to target Ansible-managed systems
- Chef Supermarket cookbook dependencies (nginx, memcached, redisio) provide functionality that will need to be replicated with equivalent Ansible modules or custom tasks