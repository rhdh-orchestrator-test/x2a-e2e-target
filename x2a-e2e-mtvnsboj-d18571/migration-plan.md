# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and system-level security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Self-signed SSL certificates for 3 subdomains (test/ci/status.cluster.local), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

**cache**:
- Description: Caching services layer providing both Redis and Memcached with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, Memcached service, custom Redis configuration cleanup via Ruby block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database/user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Currently commented out, replace with community.crypto.openssl_* modules for certificate generation

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" in cache cookbook requires Ansible Vault migration
- **PostgreSQL credentials**: FastAPI database password "fastapi_password" needs secure variable management
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands need migration to ansible.crypto modules
- **SSH security configurations**: Root login disable and password authentication disable require careful migration to maintain access
- **Firewall rules**: UFW configuration needs migration to community.general.ufw module
- **Fail2ban configuration**: Intrusion prevention rules require community.general.fail2ban module migration

### Technical Challenges

- **Ruby block workaround**: The cache cookbook contains a Ruby block hack to fix Redis configuration files - this custom logic needs reimplementation in Ansible using lineinfile or template modules
- **Complex service dependencies**: FastAPI service depends on PostgreSQL being ready, requiring proper Ansible handler and dependency management
- **Multi-site SSL configuration**: Dynamic SSL certificate generation for multiple sites needs loop-based Ansible task implementation
- **Git repository management**: FastAPI cookbook clones from GitHub, requiring ansible.builtin.git module with proper authentication handling
- **Python virtual environment**: Complex pip installation and venv management needs migration to ansible.builtin.pip module with virtualenv support

### Migration Order

1. **cache** (low risk, foundational service)
   - Straightforward package installation and service management
   - Contains the Ruby block complexity but isolated impact
   - No external service dependencies

2. **nginx-multisite** (moderate complexity, security-critical)
   - Security configurations require careful testing
   - SSL certificate generation needs validation
   - Firewall rules must maintain system access

3. **fastapi-tutorial** (high complexity, application-dependent)
   - Complex application deployment with multiple dependencies
   - Database provisioning and service orchestration
   - Git repository management and Python environment setup

### Assumptions

- Target systems will maintain the same OS family (Ubuntu/CentOS) as specified in cookbook metadata
- SSL certificates can remain self-signed for development environments (production may require Let's Encrypt or CA-signed certificates)
- PostgreSQL and Redis passwords are acceptable for development but will need proper secret management in production
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Current Chef Solo execution model can be replaced with Ansible playbook execution
- Vagrant development environment will be maintained or replaced with equivalent local testing capability
- Network connectivity and firewall rules (SSH, HTTP, HTTPS) are appropriate for target environments
- The Ruby block workaround in Redis configuration indicates potential compatibility issues that may persist in the target environment