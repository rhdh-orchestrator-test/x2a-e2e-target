# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and attribute overrides for site configurations
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Bootstrap script for Vagrant environment

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox (development), production platform not specified
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - maintain these security configurations
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - ensure proper port management in Ansible
- **Fail2ban Integration**: Jail configuration for nginx protection - maintain intrusion detection capabilities
- **Sysctl Security Tuning**: Kernel parameter hardening - preserve security configurations

### Technical Challenges

- **Custom Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or template modules
- **Multi-site SSL Certificate Generation**: Dynamic certificate generation for multiple subdomains requires careful templating and certificate lifecycle management
- **Service Dependencies**: PostgreSQL must be running before FastAPI application starts - ensure proper service ordering in Ansible playbooks
- **File Permissions and Ownership**: Complex permission schemes (ssl-cert group, www-data ownership) need careful mapping to Ansible file modules
- **Template Migration**: ERB templates need conversion to Jinja2 format, particularly nginx.conf and security configurations

### Migration Order

1. **cache** (low risk, foundational service)
   - Straightforward package installation and service management
   - Redis configuration complexity is isolated and well-defined
   
2. **nginx-multisite** (moderate complexity, security-critical)
   - Core infrastructure component with security implications
   - SSL and firewall configurations require careful validation
   
3. **fastapi-tutorial** (high complexity, application-specific)
   - Most complex with Git operations, Python environment management, and database setup
   - Depends on proper system foundation from previous modules

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in Chef metadata
- Self-signed certificates are acceptable for development; production may require proper CA-signed certificates or Let's Encrypt integration
- Current hardcoded passwords are development placeholders and will be replaced with proper secret management
- The Ruby-based Redis configuration patching is a workaround that can be replaced with proper configuration management
- Vagrant development environment will be replaced with molecule or similar Ansible testing framework
- Service user accounts (www-data, redis, postgres) exist or will be created as part of the migration
- Network connectivity requirements (PostgreSQL port 5432, Redis port 6379) remain consistent
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Current Chef Solo execution model will be replaced with standard Ansible playbook execution
- File system paths and directory structures can be maintained for compatibility