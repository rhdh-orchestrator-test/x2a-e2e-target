# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL termination for multiple subdomains (test.cluster.local, ci.cluster.local, status.cluster.local), security hardening with fail2ban and UFW firewall, and SSH configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban intrusion prevention, UFW firewall rules, SSH hardening (root login disabled, password auth disabled), sysctl security tuning

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached service, custom Redis configuration patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, ansible.builtin.template, and ansible.builtin.lineinfile modules for Redis configuration

### Security Considerations
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate using ansible.builtin.lineinfile for sshd_config
- **Firewall Configuration**: UFW rules for SSH (22), HTTP (80), HTTPS (443) - migrate using community.general.ufw module
- **Intrusion Prevention**: fail2ban configuration with custom jail.local template - migrate using ansible.builtin.template
- **System Hardening**: sysctl security parameters via template - migrate using ansible.posix.sysctl module
- **Vault/secrets management**: 
  - **nginx-multisite**: SSL certificate paths referenced but certificates not managed in cookbook
  - **cache**: Hardcoded Redis password 'redis_secure_password_123' in recipe - needs Ansible Vault
  - **fastapi-tutorial**: Hardcoded PostgreSQL password 'fastapi_password' and database credentials in .env file - needs Ansible Vault

### Technical Challenges
- **Redis Configuration Patching**: The cache cookbook uses a ruby_block hack to modify Redis config file post-installation - needs careful translation to Ansible lineinfile or replace modules
- **Multi-site SSL Management**: nginx-multisite references SSL certificate paths but doesn't manage certificate creation - migration needs to address certificate provisioning strategy
- **Database Initialization**: PostgreSQL user and database creation uses shell commands with error suppression (|| true) - needs idempotent Ansible postgresql modules
- **Git Repository Management**: FastAPI app uses git resource for code deployment - migrate to ansible.builtin.git module with proper change detection

### Migration Order
1. **cache** (low risk, standalone caching services)
2. **fastapi-tutorial** (moderate complexity, database dependencies)
3. **nginx-multisite** (high complexity, security configurations, depends on application services)

### Assumptions
- SSL certificates for nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) are managed externally or need separate certificate management solution
- The ruby_block hack in Redis configuration suggests compatibility issues with the redisio cookbook that may not exist with direct Ansible Redis management
- PostgreSQL is expected to be installed on the same host as the FastAPI application
- The target environment has internet access for git cloning and package installation
- UFW firewall rules assume standard ports and no custom application ports beyond 22, 80, 443
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- Development environment uses Vagrant, but production deployment method is not specified in the current configuration