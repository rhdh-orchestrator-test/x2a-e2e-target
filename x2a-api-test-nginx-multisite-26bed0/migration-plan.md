# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban jail configuration, UFW firewall rules, SSH security hardening, sysctl security parameters

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service setup, Redis with password authentication, custom Redis configuration patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning with Chef Solo integration
- `vagrant-provision.sh`: Bootstrap script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or VM-based deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations
- SSH hardening configurations: Migrate PermitRootLogin and PasswordAuthentication settings using ansible.posix.sshd_config module
- Firewall management: Convert UFW commands to community.general.ufw module tasks
- Fail2ban configuration: Use community.general.fail2ban module for jail management
- SSL certificate management: For each nginx site, SSL certificates and private keys need secure deployment via Ansible Vault
- Hardcoded credentials identified:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL credentials: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection strings with embedded passwords in .env files

### Technical Challenges
- **Ruby block configuration patching**: The cache cookbook uses a ruby_block to modify Redis configuration files post-installation, requiring conversion to Ansible lineinfile or template modules
- **Git repository management**: FastAPI cookbook clones from GitHub, needs conversion to ansible.builtin.git module with proper idempotency
- **Service dependency ordering**: PostgreSQL must be running before FastAPI application starts, requiring careful task ordering and handlers
- **Template conversion**: ERB templates need conversion to Jinja2 format for nginx.conf, security.conf, fail2ban.jail.local, and sysctl configurations

### Migration Order
1. **cache** (low risk, standalone caching services with clear external dependencies)
2. **nginx-multisite** (moderate complexity, security configurations but well-defined scope)
3. **fastapi-tutorial** (high complexity, database dependencies, application deployment, and service management)

### Assumptions
- SSL certificates for nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) exist and will be managed via Ansible Vault
- PostgreSQL installation and configuration requirements are limited to basic database and user creation
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Target systems have internet access for package installation and git repository cloning
- The ruby_block Redis configuration fixes in the cache cookbook address specific version compatibility issues that may not be needed with newer Redis versions
- Development and production environments will use the same OS family (Ubuntu/CentOS) as specified in cookbook metadata
- Current Chef Solo deployment model will be replaced with Ansible playbook execution, maintaining the same run list order