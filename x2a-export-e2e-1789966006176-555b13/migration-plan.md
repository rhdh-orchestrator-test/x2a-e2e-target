# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching services, a FastAPI application, and an nginx reverse proxy with SSL termination. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening, and firewall configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL-enabled virtual hosts, fail2ban integration, UFW firewall rules, SSH security hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths configured but certificate provisioning not automated - implement proper certificate management with ansible.builtin.copy or community.crypto modules
- **SSH security hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban configuration**: Custom jail configuration - migrate to community.general.fail2ban module
- **Sysctl security tuning**: Custom kernel parameter hardening - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis configuration patching**: The cache cookbook includes a Ruby block that manually patches Redis configuration files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or template modules with proper configuration management
- **Multi-site nginx configuration**: Complex template-based nginx site configuration with SSL - migrate to ansible.builtin.template with Jinja2 templates and proper site management loops
- **PostgreSQL database initialization**: Database and user creation using shell commands - migrate to community.postgresql modules for proper idempotency
- **Systemd service management**: Custom systemd service file creation and management - migrate to ansible.builtin.systemd and ansible.builtin.template modules
- **Git repository management**: FastAPI application deployment via git clone - migrate to ansible.builtin.git module with proper version control

### Migration Order

1. **cache** (moderate complexity, foundational service)
2. **fastapi-tutorial** (moderate complexity, depends on database setup)
3. **nginx-multisite** (high complexity, depends on application services, security-critical)

### Assumptions

- SSL certificates are manually managed and placed in the configured paths (/etc/ssl/certs and /etc/ssl/private) - certificate provisioning automation is not included in the current Chef configuration
- The FastAPI tutorial application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable for deployment
- PostgreSQL service configuration beyond basic installation is handled by the system defaults - no custom PostgreSQL tuning is implemented
- The target environment has internet access for package installation and git repository cloning
- UFW firewall rules assume standard port configurations (22 for SSH, 80 for HTTP, 443 for HTTPS)
- The Redis configuration patching suggests compatibility issues with the redisio cookbook version - the specific Redis version and configuration requirements need validation during migration
- Site-specific HTML files (ci/index.html, status/index.html, test/index.html) are static content that will need to be managed as Ansible files or templates
- The development environment uses Vagrant, but production deployment method is not specified in the current configuration