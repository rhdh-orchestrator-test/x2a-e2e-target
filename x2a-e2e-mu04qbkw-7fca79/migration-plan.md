# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation via community cookbook, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx, memcached, redisio) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or development environment focused

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or direct package installation and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis or geerlingguy.redis Ansible role for Redis configuration

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - maintain these security settings in Ansible
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban Integration**: Jail configuration for nginx protection - migrate to community.general.fail2ban
- **Sysctl Security Tuning**: Kernel parameter hardening via sysctl - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis Configuration Patching**: Chef cookbook includes a Ruby block that manually edits Redis config files to remove problematic lines - this hack needs proper Ansible template solution
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple domains requires Ansible loops and conditional logic
- **Database Initialization**: PostgreSQL user and database creation with proper idempotency checks
- **Service Dependencies**: Ensuring proper startup order between PostgreSQL, Redis, and application services
- **File Permissions**: Complex SSL certificate permissions (ssl-cert group) need careful Ansible file module configuration

### Migration Order

1. **cache cookbook** (low risk, foundational service) - Redis and memcached are dependencies for other services
2. **nginx-multisite cookbook** (moderate complexity) - Web server foundation needed before application deployment
3. **fastapi-tutorial cookbook** (high complexity) - Application deployment depends on database and may need reverse proxy configuration

### Assumptions

- Current Chef cookbooks are actively used in production environments requiring minimal downtime during migration
- External cookbook dependencies (nginx, memcached, redisio) from Chef Supermarket will be replaced with equivalent Ansible Galaxy roles or built-in modules
- Self-signed SSL certificates are acceptable for the target environment (development/testing) - production environments may require proper CA-signed certificates
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without service interruption
- Target systems have similar package managers and service management (systemd) as the source Chef configurations
- The Vagrant development environment setup will be maintained or replaced with equivalent Ansible-based local development tooling
- UFW firewall and fail2ban configurations are appropriate for the target environment security requirements
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible with the deployment approach