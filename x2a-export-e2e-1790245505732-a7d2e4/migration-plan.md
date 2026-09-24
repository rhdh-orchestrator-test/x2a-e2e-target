# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL management, and database setup. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, custom log directory creation, configuration file manipulation via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning (needs review for local testing strategy)
- `vagrant-provision.sh`: Vagrant provisioning script for development setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support required based on metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified in current configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks
- **PostgreSQL**: Replace with community.postgresql.* collection modules
- **Python/pip packages**: Replace with ansible.builtin.pip module

### Security Considerations

- **Hardcoded credentials**: Multiple plaintext passwords found in recipes:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env files
- **SSL certificate management**: SSL paths configured but certificate provisioning method unclear
- **SSH hardening**: Root login disabled, password authentication disabled
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH ports
- **Fail2ban integration**: Nginx protection against brute force attacks
- **Sysctl security tuning**: Kernel parameter hardening via templates

### Technical Challenges

- **Ruby block configuration manipulation**: The cache cookbook uses ruby_block to modify Redis configuration files post-installation, requiring conversion to Ansible lineinfile or template modules
- **Multi-site SSL configuration**: Complex nginx site configuration with SSL requires careful template conversion and certificate management strategy
- **Database initialization**: PostgreSQL user and database creation with proper privilege management needs idempotent Ansible tasks
- **Service dependencies**: Proper ordering of PostgreSQL → application startup requires Ansible handlers and dependency management
- **Git repository management**: FastAPI application deployment from Git requires ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, foundational service)
   - Simple package installation and service management
   - Redis configuration complexity manageable with Ansible templates

2. **nginx-multisite** (moderate complexity, security-critical)
   - Security hardening provides foundation for other services
   - SSL configuration needs careful planning but well-defined scope

3. **fastapi-tutorial** (high complexity, application-specific)
   - Depends on PostgreSQL setup and Python environment management
   - Service integration requires coordination with nginx reverse proxy setup

### Assumptions

- SSL certificates will be managed externally or via Let's Encrypt automation (current cookbook doesn't show certificate generation)
- Development environment will continue using Vagrant or migrate to container-based development
- Target environments have internet access for package installation and Git repository cloning
- PostgreSQL will be installed locally rather than using external database service
- Current hardcoded passwords are acceptable for development but will need vault integration for production
- UFW firewall is acceptable for target environments (vs. iptables or cloud security groups)
- Systemd is available on target systems for service management
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable