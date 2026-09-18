# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban intrusion prevention, UFW firewall rules, SSH security hardening, sysctl kernel parameter tuning

**cache**:
- Description: Caching services layer providing both Memcached and Redis with authentication, custom Redis configuration patching, and log directory management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication, custom Redis config file manipulation, log directory creation

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, including virtual environment setup, systemd service management, and database initialization
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for development setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks
- **PostgreSQL**: Replace with community.postgresql.* collection modules
- **Python/pip packages**: Replace with ansible.builtin.pip module
- **Git repository management**: Replace with ansible.builtin.git module

### Security Considerations

- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL password ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths are configured but certificate provisioning method unclear - requires SSL certificate deployment strategy
- **SSH security hardening**: Root login disable and password authentication disable configurations need careful migration
- **Firewall rules**: UFW firewall configuration with specific port allowances (SSH, HTTP, HTTPS)
- **Fail2ban configuration**: Intrusion prevention system configuration via template
- **Sysctl security parameters**: Kernel parameter tuning for security hardening

### Technical Challenges

- **Redis configuration patching**: The cache cookbook includes a Ruby block that manually edits Redis config files to remove specific directives - this hack-style approach needs proper Ansible template-based solution
- **Multi-site SSL configuration**: Complex nginx virtual host setup with SSL for multiple subdomains requires careful template migration
- **Database initialization**: PostgreSQL user and database creation with proper privilege assignment needs idempotent Ansible tasks
- **Systemd service management**: FastAPI application systemd service creation and management requires proper Ansible service module usage
- **File permissions and ownership**: Multiple cookbooks manage file ownership (www-data, redis, root) requiring careful Ansible file module configuration

### Migration Order

1. **cache** (low risk, foundational service) - Memcached and Redis setup with authentication
2. **nginx-multisite** (moderate complexity) - Web server with security hardening and multi-site configuration  
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- SSL certificates are managed externally or through a separate process not visible in the current cookbooks
- The development environment (Vagrant) configuration will be replaced with molecule testing or similar Ansible testing framework
- External cookbook dependencies (nginx, memcached, redisio) functionality will be replicated using Ansible modules rather than including equivalent Ansible Galaxy roles
- The target environment supports systemd for service management (implied by FastAPI systemd service configuration)
- PostgreSQL installation and initial configuration is handled by the system package manager
- The Ruby-based Redis configuration patching indicates potential configuration drift issues that should be resolved with proper templating in Ansible