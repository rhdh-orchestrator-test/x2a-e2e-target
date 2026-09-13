# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW firewall, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services layer providing both Redis and Memcached with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, Memcached service, custom Redis configuration cleanup via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service integration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with attribute overrides for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Vagrant provisioning script for development setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Solo execution model**: Replace with Ansible playbook execution targeting localhost or remote hosts

### Security Considerations
- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules
- **SSH hardening configurations**: Root login disable and password authentication disable require careful migration to avoid lockout
- **Firewall rules**: UFW commands need migration to community.general.ufw module
- **Fail2ban configuration**: Template-based jail.local configuration requires Ansible template migration
- **File permissions**: SSL private key permissions (640, ssl-cert group) need proper Ansible file module configuration

### Technical Challenges
- **Ruby block workarounds**: The Redis configuration cleanup ruby_block in cache cookbook requires reimplementation as Ansible lineinfile or replace tasks
- **Complex service dependencies**: PostgreSQL must be running before database/user creation, requiring proper Ansible task ordering with handlers
- **Multi-site SSL certificate generation**: Loop-based certificate creation for multiple sites needs Ansible with_items implementation
- **Git repository synchronization**: FastAPI tutorial Git cloning with revision tracking requires ansible.builtin.git module configuration
- **Python virtual environment management**: Virtual environment creation and pip dependency installation requires ansible.builtin.pip module with virtualenv parameters
- **Systemd service template**: Complex multi-line systemd service file requires Ansible template conversion

### Migration Order
1. **cache** (low risk, foundational service) - Redis and Memcached services with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Python application with database dependencies, requires cache services
3. **nginx-multisite** (high complexity, security-critical) - Reverse proxy with SSL, security hardening, and firewall configuration that fronts other services

### Assumptions
- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- PostgreSQL installation method (package vs. source) is flexible and can use distribution packages
- Redis and Memcached can use distribution packages rather than custom compilation
- UFW firewall is the preferred firewall solution (vs. iptables direct configuration)
- SSH service name consistency across target distributions (may be 'ssh' vs 'sshd')
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available during migration
- Python 3 virtual environment tools are available on target systems
- Systemd is the target init system (no SysV init support required)
- File ownership patterns (www-data user/group) are consistent across target distributions