# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached integration, Redis with password authentication, custom Redis configuration patching, log directory management

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
- `solo.json`: Chef Solo run configuration with site-specific attributes and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall Rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS) - migrate to ansible.posix.ufw module
- **Fail2ban Configuration**: Custom jail.local template for intrusion prevention - migrate template to Jinja2
- **Sysctl Security Tuning**: Custom kernel parameter hardening via template - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this complex logic needs careful translation to Ansible lineinfile or replace modules
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple domains requires loop-based certificate creation in Ansible
- **Service Dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper service ordering with handlers
- **File Permissions**: Complex SSL certificate permissions (ssl-cert group) need careful mapping to Ansible file module
- **Template Migration**: ERB templates need conversion to Jinja2 format with proper variable substitution

### Migration Order

1. **cache** (low risk, foundational service)
   - Simple package installation and service management
   - Redis configuration complexity can be isolated and tested independently

2. **nginx-multisite** (moderate complexity, security-critical)
   - Core web infrastructure with security hardening
   - SSL and firewall configurations require careful validation

3. **fastapi-tutorial** (high complexity, application-specific)
   - Complex application deployment with database dependencies
   - Git integration and Python environment management
   - Service orchestration dependencies

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require proper CA certificates)
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without changing the actual credential values
- The Ruby-based Redis configuration patching represents a workaround that may not be needed with proper Redis module usage in Ansible
- Vagrant development environment will be replaced with equivalent Ansible testing setup
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with native Ansible modules and community collections
- Site-specific attributes in solo.json represent the desired production configuration values
- The fail2ban and sysctl templates contain standard security configurations that can be generalized for Ansible deployment