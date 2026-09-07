# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW firewall, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening (root login disabled, password auth disabled), sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services configuration providing both Redis and Memcached with authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, Memcached service, custom Redis configuration cleanup via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo node configuration with run_list and attribute overrides for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning configuration for local testing
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Currently commented out, replace with community.crypto.openssl_* modules for certificate management

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - migrate to community.crypto collection for proper certificate lifecycle management
- **SSH Security Configuration**: Root login disabled and password authentication disabled via direct file manipulation - migrate to ansible.posix.sshd_config module
- **Firewall Rules**: UFW firewall rules managed via shell commands - migrate to community.general.ufw module
- **Fail2ban Configuration**: Template-based jail configuration - migrate to community.general.fail2ban module
- **Database Credentials**: PostgreSQL user creation with embedded passwords - migrate to community.postgresql.postgresql_* modules with Ansible Vault

### Technical Challenges

- **Ruby Block Workarounds**: The cache cookbook contains a ruby_block hack to fix Redis configuration by removing specific lines - this custom logic needs to be replicated using Ansible's lineinfile or replace modules
- **Multi-site SSL Configuration**: Dynamic SSL certificate generation for multiple sites requires careful templating and certificate lifecycle management in Ansible
- **Service Dependencies**: Complex service startup order (PostgreSQL before FastAPI, nginx after SSL certificates) needs proper Ansible handler and dependency management
- **Git Repository Management**: FastAPI application deployment via git clone needs migration to ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, high value) - Simple service installation with well-defined external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but straightforward service management
3. **nginx-multisite** (high complexity, dependencies) - Complex multi-site configuration with SSL, security hardening, and firewall management

### Assumptions

- The target environment will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+)
- Self-signed certificates are acceptable for development environments (production would require proper CA-signed certificates)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Current hardcoded passwords are acceptable for development but will be migrated to Ansible Vault for production
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the complete scope of required virtual hosts
- PostgreSQL and Redis services will continue to run on the same host as the web services (no external database migration required)
- The ruby_block workaround in the Redis configuration indicates compatibility issues with the redisio cookbook that may not exist with direct Ansible Redis management