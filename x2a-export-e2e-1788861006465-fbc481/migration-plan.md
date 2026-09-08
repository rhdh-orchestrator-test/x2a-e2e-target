# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services configuration with Redis authentication and Memcached, including custom Redis configuration fixes for compatibility
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, Memcached service, custom Redis configuration patching via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and attribute overrides for site-specific settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified (local development focus)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Solo**: Replace with ansible-playbook execution model

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Security Configuration**: Root login disabled, password authentication disabled - migrate using ansible.posix.sysctl and lineinfile modules
- **Firewall Rules**: UFW configuration for ports 22, 80, 443 - migrate using community.general.ufw module
- **Fail2ban Configuration**: Intrusion prevention via template - migrate using ansible.builtin.template module
- **Database Credentials**: PostgreSQL user/password creation via shell commands - migrate to community.postgresql.postgresql_* modules with vault integration

### Technical Challenges

- **Ruby Block Workarounds**: The cache cookbook contains a ruby_block that manually edits Redis configuration files to remove incompatible directives - this will need custom Ansible tasks with lineinfile or replace modules
- **Chef Template Variables**: ERB templates with Chef node attributes need conversion to Jinja2 templates with Ansible variables
- **Service Dependencies**: Complex service restart notifications and dependencies need careful ordering in Ansible playbooks
- **Multi-site SSL Configuration**: Dynamic SSL certificate generation and nginx site configuration requires Ansible loops and conditional logic
- **Git Repository Management**: FastAPI application deployment via git clone needs idempotent handling using ansible.builtin.git module

### Migration Order

1. **cache** (low risk, foundational service) - Redis and Memcached services with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Python application with database dependencies but straightforward systemd service
3. **nginx-multisite** (high complexity, depends on other services) - Complex multi-site configuration with SSL, security hardening, and integration with backend services

### Assumptions

- Current Chef cookbooks target Ubuntu/CentOS environments - Ansible playbooks will maintain this multi-platform support
- Self-signed certificates are acceptable for development environments - production deployment may require Let's Encrypt or CA-signed certificates
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without changing the application configuration
- The ruby_block workaround in the Redis configuration indicates compatibility issues that may persist and require similar manual configuration in Ansible
- Vagrant development environment will be replaced with equivalent Ansible provisioning or molecule testing framework
- The Chef Solo execution model suggests single-node deployment - Ansible playbooks should support both single-node and multi-node scenarios
- Static HTML files in cookbooks/nginx-multisite/files/ are simple placeholder content and don't require complex templating
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) is accessible and stable for automated deployment
- Current firewall and security configurations are appropriate for the target environment and don't require significant changes during migration