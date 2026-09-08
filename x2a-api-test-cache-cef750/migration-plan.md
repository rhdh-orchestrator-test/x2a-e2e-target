# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis 6379 with authentication, custom log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication (redis_secure_password_123), custom log directory creation, configuration file manipulation via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning from GitHub, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration, environment file with database credentials

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL termination for multiple subdomains, security hardening with fail2ban/UFW, and comprehensive security headers
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and attribute overrides for site-specific settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Shell script for Vagrant VM setup and Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence for development)
- **Cloud Platform**: Not specified (local development focus with potential cloud deployment)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration tasks

### Security Considerations

- **Hardcoded credentials in recipes**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi_password) are embedded in recipe files - migrate to Ansible Vault
- **SSL certificate management**: SSL certificates referenced in templates need secure deployment mechanism via Ansible Vault or certificate automation
- **SSH security configuration**: Root login disabling and password authentication disabling require careful migration to avoid lockout
- **Database credentials**: PostgreSQL user creation with embedded passwords needs Ansible Vault integration
- **Environment files**: FastAPI .env file contains database connection strings with credentials

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses ruby_block to manipulate Redis configuration files post-installation - requires conversion to Ansible lineinfile or template modules
- **Complex nginx site templating**: Multi-site SSL configuration with conditional SSL blocks needs careful Jinja2 template conversion
- **Service dependency orchestration**: PostgreSQL must be running before database user creation, and systemd reload must occur before service start
- **Git repository cloning with dependency installation**: FastAPI cookbook clones repository and installs Python dependencies in sequence - requires proper Ansible task ordering
- **UFW firewall rule idempotency**: Current implementation uses shell commands with conditional checks - migrate to community.general.ufw module

### Migration Order

1. **cache cookbook** (low risk, isolated caching services)
2. **fastapi-tutorial cookbook** (moderate complexity, database dependencies)
3. **nginx-multisite cookbook** (high complexity, security configurations and multi-site SSL)

### Assumptions

- SSL certificates are manually managed and placed in /etc/ssl/certs and /etc/ssl/private directories
- The FastAPI tutorial repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Target systems have internet access for package installation and git repository cloning
- PostgreSQL service configuration beyond basic installation is handled externally
- The three subdomain sites (test.cluster.local, ci.cluster.local, status.cluster.local) are intended for internal cluster communication
- Current Chef Solo execution model will be replaced with Ansible playbook execution
- Development workflow using Vagrant will be maintained or replaced with equivalent Ansible testing approach
- Security hardening configurations (fail2ban, UFW, SSH) are appropriate for the target environment
- Redis configuration patching via ruby_block indicates potential compatibility issues with the redisio cookbook that may not exist in Ansible redis modules