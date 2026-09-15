# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and nginx multi-site hosting with SSL. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Configures caching services including memcached and Redis with authentication, custom log directories, and configuration fixes for Redis compatibility
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached integration, Redis with password authentication (redis_secure_password_123), custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI tutorial application deployment with PostgreSQL database, Python virtual environment, systemd service management, and Git-based source deployment
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, PostgreSQL database and user creation, systemd service configuration, Git repository cloning, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban and UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external cookbooks from Chef Supermarket (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and node configuration
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules for memcached installation and management
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, ansible.builtin.template, and ansible.builtin.service modules for Redis configuration and management

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL password (fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled and password authentication disabled via direct file modification - migrate to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules managed via execute resources - migrate to community.general.ufw module
- **Fail2ban configuration**: Template-based jail configuration - migrate to ansible.builtin.template with proper handlers
- **Database credentials**: PostgreSQL user and database creation with embedded passwords - migrate to Ansible Vault and postgresql modules

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis configuration files post-installation - requires conversion to Ansible lineinfile or template modules with proper configuration management
- **Execute resource dependencies**: Multiple execute resources for database setup, SSL certificate generation, and system configuration - need proper Ansible task ordering and idempotency checks
- **Template and static file management**: ERB templates and static HTML files need conversion to Jinja2 templates and Ansible file management
- **Service dependency management**: Complex service restart notifications and dependencies need conversion to Ansible handlers and proper task ordering

### Migration Order

1. **cache** (low risk, high value) - Straightforward package installation and service management with well-defined external dependencies
2. **nginx-multisite** (moderate complexity) - Security configurations and multi-site management require careful template conversion and handler setup
3. **fastapi-tutorial** (high complexity, dependencies) - Application deployment with database setup, virtual environments, and systemd service management

### Assumptions

- Target environment will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Current hardcoded passwords are acceptable for development but will need Ansible Vault for production
- Self-signed certificates are sufficient for the target environment (no Let's Encrypt integration required initially)
- PostgreSQL and Redis services will continue to run on the same hosts as the applications
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Vagrant-based development workflow will be maintained or replaced with equivalent local development setup
- Current firewall rules (SSH, HTTP, HTTPS) are sufficient for the target environment
- The ruby_block configuration fixes in the Redis setup indicate compatibility issues that may need addressing in the Ansible version
- Static HTML files for test sites (ci, status, test) are simple placeholders and don't require dynamic content generation