# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom configuration fixes
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
- `solo.json`: Chef Solo run list and node attributes configuration for all three services
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve in Ansible tasks
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban integration**: Jail configuration for nginx protection - migrate to community.general.fail2ban
- **Sysctl security tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module
- **Credential types per module**:
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded)
  - nginx-multisite: SSL certificate generation (self-signed)

### Technical Challenges

- **Redis configuration patching**: The cache cookbook includes a Ruby block that manually edits Redis config files to remove specific directives - this will need custom Ansible tasks with lineinfile or template modules
- **Multi-site SSL management**: Dynamic SSL certificate generation for multiple domains requires loop-based Ansible tasks with proper certificate validation
- **Service orchestration**: Dependencies between PostgreSQL, Redis, and nginx services need proper Ansible handlers and task ordering
- **Template migration**: ERB templates need conversion to Jinja2 format for nginx.conf, security.conf, and fail2ban configurations
- **Git repository management**: FastAPI application deployment from Git requires ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, standalone service)
   - Migrate memcached and Redis installation
   - Convert Redis configuration patching logic
   - Test caching functionality independently

2. **fastapi-tutorial** (moderate complexity, database dependencies)
   - Migrate PostgreSQL installation and configuration
   - Convert Python application deployment
   - Implement systemd service management
   - Test application startup and database connectivity

3. **nginx-multisite** (high complexity, security dependencies)
   - Migrate nginx installation and configuration
   - Convert security hardening tasks (fail2ban, UFW, SSH)
   - Implement SSL certificate management
   - Convert multi-site configuration with proper templating
   - Test complete web stack integration

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in Chef metadata
- Self-signed certificates are acceptable for development; production may require proper CA-signed certificates or Let's Encrypt integration
- Current hardcoded passwords are development placeholders and will be replaced with Ansible Vault secrets
- The Ruby-based Redis configuration patching is a workaround that can be replaced with proper Redis configuration management
- Vagrant development environment will be replaced with molecule or similar Ansible testing framework
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with native Ansible modules and community collections
- Service startup order dependencies are implicit in Chef and will need explicit definition in Ansible playbooks
- File ownership and permissions (www-data user, ssl-cert group) are consistent across target platforms