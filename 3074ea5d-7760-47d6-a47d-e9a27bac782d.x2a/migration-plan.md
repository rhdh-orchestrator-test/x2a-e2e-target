# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation via external cookbook, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx, memcached, redisio) and local cookbook paths
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning for testing cookbook functionality
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning and Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration templates

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled and password authentication disabled via direct file modification - use ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules managed via shell commands - migrate to community.general.ufw module
- **Fail2ban Integration**: Template-based configuration - convert to ansible.builtin.template with proper handlers
- **Credential Types per Module**:
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded)
  - nginx-multisite: SSL certificate generation (self-signed, no stored secrets)

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be replaced with proper template management in Ansible
- **Multi-Site SSL Management**: Dynamic SSL certificate generation for multiple sites requires careful loop handling and certificate validation in Ansible
- **Service Dependencies**: PostgreSQL must be running before database creation, and nginx must reload after configuration changes - requires proper Ansible handlers and task ordering
- **Git Repository Management**: FastAPI application deployment via git clone needs idempotent handling and proper change detection

### Migration Order

1. **cache** (moderate complexity, standalone caching services with external dependencies)
2. **fastapi-tutorial** (moderate complexity, application deployment with database setup)
3. **nginx-multisite** (high complexity, multi-site configuration with security hardening and SSL management)

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- External cookbook dependencies (nginx, memcached, redisio) functionality will be replicated using Ansible modules rather than direct cookbook translation
- Self-signed certificates are acceptable for the target environment, or proper CA-signed certificates will be provided separately
- PostgreSQL and Redis services will continue to run on the same hosts as the applications
- The current Chef Solo execution model will be replaced with Ansible playbook execution
- Vagrant development environment setup will be maintained for testing migrated Ansible playbooks
- Network connectivity requirements (HTTP/HTTPS/SSH ports) will remain the same in the target environment
- The Ruby-based configuration patching in the Redis setup indicates potential configuration drift issues that should be addressed with proper template management in Ansible