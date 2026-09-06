# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI tutorial application with PostgreSQL backend. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including hardcoded credentials.

**Migration Complexity**: Medium-High  
**Estimated Timeline**: 3-4 weeks  
**Team Coordination Required**: DevOps, Security, and Application teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL termination, multi-site configuration, security hardening (fail2ban, UFW firewall), and self-signed certificate generation for development environments
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: SSL-enabled virtual hosts for test.cluster.local, ci.cluster.local, and status.cluster.local; fail2ban intrusion prevention; UFW firewall configuration; SSH hardening; sysctl security tuning; custom lineinfile resource

- **cache**:
    - Description: Caching services configuration with Memcached and Redis, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service setup, Redis with password authentication (redis_secure_password_123), custom Redis configuration cleanup via ruby_block, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook references
- `solo.json`: Chef Solo run list configuration and node attributes including nginx site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, network configuration (192.168.121.10), and port forwarding (80→8080, 443→8443)
- `vagrant-provision.sh`: Automated Chef installation and cookbook dependency resolution using Berkshelf

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for Ansible migration.
- **Virtual Machine Technology**: KVM/libvirt (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules for configuration management
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules for memcached installation and management
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Ansible tasks for Redis configuration with authentication
- **Chef Berkshelf**: Replace with Ansible Galaxy for role dependency management (ansible-galaxy requirements.yml)

### Security Considerations

- **Hardcoded Credentials**: Critical security issue - Redis password 'redis_secure_password_123' is hardcoded in cookbooks/cache/recipes/default.rb. Migration approach: Move to Ansible Vault encrypted variables
- **PostgreSQL Credentials**: Database password 'fastapi_password' is hardcoded in cookbooks/fastapi-tutorial/recipes/default.rb. Migration approach: Use Ansible Vault for database credentials
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands. Migration approach: Use community.crypto.openssl_* modules for certificate generation and management
- **SSH Hardening**: Root login disabled, password authentication disabled via direct file modification. Migration approach: Use ansible.posix.sshd_config module for SSH configuration management
- **Firewall Configuration**: UFW firewall rules managed via shell commands. Migration approach: Use community.general.ufw module for declarative firewall management
- **Fail2ban Configuration**: Template-based jail configuration. Migration approach: Use community.general.fail2ban module or template management

**Vault/secrets management**: 
- **nginx-multisite**: 0 hardcoded credentials detected (uses self-signed certificates)
- **cache**: 1 hardcoded credential - Redis password in recipe file
- **fastapi-tutorial**: 2 hardcoded credentials - PostgreSQL user password and database connection string in .env file

### Technical Challenges

- **Custom Ruby Block Logic**: The cache cookbook contains a ruby_block resource that performs complex Redis configuration file manipulation. Migration approach: Convert to Ansible lineinfile or template modules with equivalent logic
- **Custom Chef Resource**: nginx-multisite cookbook defines a custom 'lineinfile' resource in resources/lineinfile.rb. Migration approach: Replace with ansible.builtin.lineinfile module which provides similar functionality
- **Template Dependencies**: Multiple ERB templates need conversion to Jinja2 format (nginx.conf.erb, site.conf.erb, security.conf.erb, fail2ban.jail.local.erb, sysctl-security.conf.erb)
- **Git Repository Cloning**: Chef git resource needs replacement with ansible.builtin.git module for FastAPI application deployment
- **Systemd Service Management**: Custom systemd service file creation and management needs conversion to ansible.builtin.systemd module
- **Package Installation Variations**: Cookbooks support both Ubuntu and CentOS - Ansible playbooks need conditional package management for different OS families

### Migration Order

1. **cache** (Priority 1 - low complexity, foundational service)
   - Simple service installation and configuration
   - Address Redis password security issue first
   - No dependencies on other cookbooks

2. **fastapi-tutorial** (Priority 2 - moderate complexity, application layer)
   - Database setup and application deployment
   - Depends on system packages but not other cookbooks
   - Address PostgreSQL credential security

3. **nginx-multisite** (Priority 3 - high complexity, multiple integrations)
   - Complex multi-site configuration with SSL
   - Security hardening across multiple services
   - Custom resource conversion required
   - Integration point for other services

### Assumptions

- Target environment will maintain the same OS support (Ubuntu 18.04+ or CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production would require proper CA-signed certificates)
- The FastAPI tutorial application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Current network configuration (192.168.121.10 with port forwarding) is suitable for the target environment
- Vagrant-based development workflow will be replaced with Ansible-based provisioning
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with native Ansible modules
- The ruby_block configuration fixes in the cache cookbook are still necessary for Redis operation
- Site-specific static files (test/index.html, ci/index.html, status/index.html) will be migrated as-is
- Current security hardening requirements (fail2ban, UFW, SSH configuration, sysctl tuning) remain applicable
- PostgreSQL and Redis services will continue to run on the same host as the web services
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the complete scope of required virtual hosts