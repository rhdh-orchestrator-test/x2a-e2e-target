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
- `solo.json`: Chef Solo configuration with run_list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Shell script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant-based development environment (VirtualBox/VMware likely)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks

### Security Considerations
- SSH hardening configurations: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- Firewall management: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- Fail2ban configuration: Custom jail.local template - migrate to community.general.ini_file or template module
- SSL certificate management: Certificate and private key paths configured - requires Ansible vault or certificate automation
- Credential patterns identified:
  - Redis password hardcoded in recipe: 'redis_secure_password_123'
  - PostgreSQL credentials hardcoded: 'fastapi_password'
  - Database connection string with embedded credentials in .env file
  - SSL certificate paths requiring secure file deployment

### Technical Challenges
- **Ruby block configuration patching**: The cache cookbook uses a ruby_block to modify Redis configuration files post-installation - requires conversion to Ansible lineinfile or replace modules
- **Git repository management**: FastAPI cookbook clones from GitHub - needs conversion to ansible.builtin.git module with proper idempotency
- **Multi-site nginx configuration**: Template-driven virtual host generation needs conversion to Ansible jinja2 templates with loop constructs
- **Service dependency management**: PostgreSQL must be running before FastAPI application starts - requires proper Ansible handler and dependency ordering

### Migration Order
1. **cache** (low risk, standalone caching services with clear external dependencies)
2. **nginx-multisite** (moderate complexity, security configurations but well-defined scope)
3. **fastapi-tutorial** (highest complexity, database setup, application deployment, and service management)

### Assumptions
- SSL certificates are manually managed or obtained externally (no Let's Encrypt automation detected in current configuration)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Current hardcoded passwords are acceptable for development environments but will need Ansible Vault integration for production
- The nginx external cookbook version ~> 12.0 provides compatible configuration patterns that can be replicated in Ansible
- UFW and fail2ban packages are available in target OS repositories
- PostgreSQL version compatibility is maintained across Chef and Ansible deployments
- The custom Redis configuration patching in the ruby_block is still necessary and not resolved by newer Redis versions