# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with Redis authentication and Memcached setup, includes Redis log directory management and configuration file patching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached integration, custom Redis configuration patching, log directory setup

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service management, environment configuration

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-domain hosting, security hardening, and fail2ban protection
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: SSL/TLS termination, multiple virtual hosts, security headers, fail2ban integration, UFW firewall, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations
- **Hardcoded credentials**: Redis password 'redis_secure_password_123' and PostgreSQL password 'fastapi_password' are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificates referenced in templates need secure deployment strategy
- **SSH security**: Root login disabled and password authentication disabled - preserve in Ansible
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH need translation to ansible.posix.firewalld or ufw modules
- **Fail2ban integration**: Jail configuration templates need migration to Ansible template module
- **Security headers**: Comprehensive HTTP security headers in nginx configuration must be preserved

### Technical Challenges
- **Redis configuration patching**: Complex ruby_block hack for Redis config file modification needs clean Ansible template-based solution
- **Multi-site SSL configuration**: ERB templates with conditional SSL logic require Jinja2 template conversion
- **Service orchestration**: Complex service dependencies (PostgreSQL → FastAPI → Nginx) need proper Ansible handler chains
- **Git repository management**: FastAPI application deployment from Git requires ansible.builtin.git module with proper change detection
- **Database initialization**: PostgreSQL user and database creation with idempotency checks needs postgresql_* modules

### Migration Order
1. **cache** (low risk, standalone service with clear dependencies)
2. **fastapi-tutorial** (moderate complexity, database and application deployment)
3. **nginx-multisite** (high complexity, security configurations and SSL management)

### Assumptions
- SSL certificates are manually managed and available at specified paths (/etc/ssl/certs, /etc/ssl/private)
- PostgreSQL service is expected to be available on the target system
- The FastAPI tutorial Git repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible
- Target systems have internet connectivity for package installation and Git cloning
- Current Chef Solo execution model will be replaced with Ansible playbook execution
- Site-specific HTML files (ci/index.html, status/index.html, test/index.html) are static and don't require dynamic generation
- UFW firewall is the preferred firewall solution (vs firewalld on RHEL systems)
- The 'www-data' user exists on target systems for nginx file ownership
- Systemd is available for service management on target systems