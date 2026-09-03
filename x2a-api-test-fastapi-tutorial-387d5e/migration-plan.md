# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates, firewall rules, and database credentials.

**Migration Complexity**: Medium-High (3 cookbooks, external dependencies, security configurations, SSL management)
**Estimated Timeline**: 3-4 weeks (1 week per cookbook + integration testing)
**Team Coordination**: Requires coordination between web infrastructure, security, and application teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Multi-site nginx web server with SSL termination, security hardening (fail2ban, UFW firewall), and custom site configurations for test.cluster.local, ci.cluster.local, and status.cluster.local domains
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Self-signed SSL certificate generation, fail2ban intrusion prevention, UFW firewall configuration, SSH hardening (root login disabled, password auth disabled), sysctl security tuning, custom lineinfile resource, nginx site management with SSL

- **cache**:
    - Description: Caching layer services providing both Memcached and Redis with authentication, including Redis configuration fixes and log directory management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service via external cookbook, Redis with password authentication (redis_secure_password_123), custom Redis configuration cleanup, log directory creation with proper ownership

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database backend, including virtual environment setup, systemd service management, and database initialization
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 virtual environment, Git repository cloning from https://github.com/dibanez/fastapi_tutorial.git, PostgreSQL database and user creation, systemd service configuration, environment file management with database credentials

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths. Migration requires replacing with Ansible Galaxy requirements.yml or collections.
- `solo.json`: Chef node attributes defining nginx site configurations, SSL paths, and security settings. Migration requires converting to Ansible group_vars or host_vars YAML files.
- `solo.rb`: Chef Solo configuration specifying cookbook paths and logging. Migration requires Ansible configuration in ansible.cfg.
- `Vagrantfile`: Development environment using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443), and rsync folder sync. Migration requires updating provisioner from Chef to Ansible.
- `vagrant-provision.sh`: Chef installation and Berkshelf dependency management script. Migration requires replacing with Ansible installation and galaxy collection management.

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations). Primary development environment uses Fedora 42 (from Vagrantfile). Recommend standardizing on Ubuntu 20.04 LTS for production.
- **Virtual Machine Technology**: libvirt/KVM (based on Vagrantfile provider configuration with 2GB RAM, 2 CPUs)
- **Cloud Platform**: Not specified - appears to be on-premises or local development environment based on private network configuration (192.168.121.10)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules for configuration management
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules, plus configuration templates
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks with ansible.builtin.template
- **Chef Supermarket cookbooks**: All external dependencies need replacement with Ansible Galaxy collections or custom role implementations

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands needs migration to community.crypto.openssl_* modules for proper certificate lifecycle management
- **Firewall Configuration**: UFW firewall rules implemented via shell commands need migration to community.general.ufw module for idempotent management
- **SSH Hardening**: Direct sshd_config file manipulation needs migration to ansible.posix.sshd_config module for safer SSH configuration
- **Fail2ban Configuration**: Template-based jail.local configuration needs migration to community.general.fail2ban module
- **Vault/secrets management**: 
  - **nginx-multisite**: No hardcoded credentials detected, SSL certificates are self-signed and generated
  - **cache**: 1 hardcoded credential detected - Redis password 'redis_secure_password_123' in recipes/default.rb
  - **fastapi-tutorial**: 2 hardcoded credentials detected - PostgreSQL user password 'fastapi_password' and database connection string in .env file
  - **Total credentials requiring vault migration**: 3 credentials across 2 modules

### Technical Challenges

- **Custom Chef Resource Migration**: The lineinfile.rb custom resource needs replacement with ansible.builtin.lineinfile module, requiring logic translation from Ruby to YAML
- **Redis Configuration Cleanup**: Complex Ruby block performing regex-based configuration file cleanup needs migration to ansible.builtin.replace tasks with proper pattern matching
- **Multi-site SSL Management**: Dynamic SSL certificate generation per site requires Ansible loops with community.crypto modules and proper certificate validation
- **Database Initialization**: PostgreSQL user and database creation using shell commands needs migration to community.postgresql.* modules for proper idempotency
- **Systemd Service Management**: Template-based systemd service file creation needs migration to ansible.builtin.template with proper service restart handlers
- **Git Repository Cloning**: FastAPI application deployment from Git needs migration to ansible.builtin.git module with proper version control

### Migration Order

1. **cache** (Priority 1 - low risk, high value): Simple service installation with minimal external dependencies, good starting point for team familiarity
2. **nginx-multisite** (Priority 2 - moderate complexity): Core web infrastructure with security configurations, requires careful SSL and firewall migration
3. **fastapi-tutorial** (Priority 3 - high complexity, dependencies): Application deployment with database dependencies, requires coordination with application team and database administrators

### Assumptions

- **Operating System Standardization**: Assuming migration will standardize on Ubuntu 20.04 LTS despite current multi-OS support (Ubuntu 18.04+, CentOS 7+, Fedora 42 development)
- **SSL Certificate Strategy**: Assuming self-signed certificates are acceptable for development/testing environments, production may require Let's Encrypt or corporate CA integration
- **Database Credentials**: Assuming hardcoded database passwords are acceptable for development, production will require Ansible Vault or external secret management
- **Network Configuration**: Assuming current private network setup (192.168.121.10) is suitable for migration, may need adjustment for different virtualization platforms
- **External Repository Access**: Assuming continued access to https://github.com/dibanez/fastapi_tutorial.git for application deployment
- **Service Dependencies**: Assuming PostgreSQL service startup order dependencies are correctly handled in current Chef implementation
- **File Permissions**: Assuming current file ownership patterns (www-data, redis user, ssl-cert group) are appropriate for target environment
- **Vagrant Development Environment**: Assuming Vagrant-based development workflow will continue post-migration with Ansible provisioner
- **Chef License Acceptance**: Current implementation uses CHEF_LICENSE=accept-silent, migration removes this licensing requirement
- **Berkshelf Dependency Resolution**: Assuming all external cookbook dependencies have equivalent Ansible Galaxy collections or can be implemented as custom tasks