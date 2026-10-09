# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, memcached integration, Redis log directory management, configuration file patching

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and SSH configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - maintain these security settings in Ansible
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to ansible.posix.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate template to Jinja2 format
- **Sysctl security parameters**: Custom security.conf template - migrate to ansible.posix.sysctl module
- **Credential types per module**:
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded)
  - nginx-multisite: SSL certificate generation (self-signed, no stored credentials)

### Technical Challenges

- **Redis configuration patching**: The cache cookbook uses a Ruby block to manually edit Redis configuration files - this hack needs to be replaced with proper Redis configuration management in Ansible
- **Multi-site SSL management**: Dynamic SSL certificate generation for multiple sites requires careful templating and certificate lifecycle management
- **Service dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper service ordering and health checks
- **File permissions and ownership**: Complex SSL certificate permissions (ssl-cert group) need careful mapping to Ansible file module parameters
- **Git repository management**: FastAPI cookbook clones from GitHub - ensure proper Git module usage with appropriate authentication if needed

### Migration Order

1. **cache** (low risk, high value) - Straightforward service installation with known Redis configuration challenges
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but well-defined service boundaries
3. **nginx-multisite** (high complexity, dependencies) - Complex multi-site configuration with SSL, security hardening, and multiple interdependent components

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as defined in cookbook metadata
- External cookbook dependencies (nginx, memcached, redisio) can be replaced with equivalent Ansible modules or community collections
- The Vagrant development environment will be replaced with an equivalent Ansible-based local testing setup
- SSL certificates will continue to use self-signed certificates for development, with production certificate management to be defined separately
- The current hardcoded passwords are acceptable for development environments but will need proper secret management for production
- Network connectivity and package repository access remain the same as the current Chef-managed environment
- The Ruby-based configuration patching in the Redis setup indicates potential configuration management issues that may require deeper investigation of the underlying Redis cookbook behavior
- Service user accounts (www-data, redis, postgres) are assumed to exist or be created by package installation as in the current setup