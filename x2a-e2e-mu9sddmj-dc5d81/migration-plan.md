# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

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
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration templates

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - maintain these security configurations
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - preserve firewall rules in Ansible
- **Fail2ban Configuration**: Jail configuration for intrusion prevention - migrate fail2ban templates and configuration
- **Sysctl Security Tuning**: Kernel parameter hardening via sysctl - maintain security parameter configurations
- **Credential Types per Module**:
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded), application environment variables
  - nginx-multisite: SSL certificate paths, no embedded credentials but certificate generation

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific parameters - this custom logic needs to be replicated in Ansible using lineinfile or template modules
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple sites based on node attributes requires careful templating and certificate management in Ansible
- **Service Dependencies**: PostgreSQL must be running before database creation, nginx must reload after configuration changes - ensure proper task ordering and handlers
- **Cross-cookbook Dependencies**: The nginx-multisite cookbook orchestrates multiple recipes (security, nginx, ssl, sites) that must be executed in proper order

### Migration Order

1. **cache** (low risk, standalone service)
2. **fastapi-tutorial** (moderate complexity, database dependencies)
3. **nginx-multisite** (high complexity, multiple security configurations and SSL management)

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require proper CA-signed certificates)
- Current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault post-migration)
- PostgreSQL installation and configuration is handled by system packages rather than dedicated cookbook
- The Ruby-based Redis configuration patching represents a workaround that may not be needed with proper Redis configuration templates
- Vagrant development environment will be maintained or replaced with equivalent Ansible-based development setup
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with native Ansible modules and community collections