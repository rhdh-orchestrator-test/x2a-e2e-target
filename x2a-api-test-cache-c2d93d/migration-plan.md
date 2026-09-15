# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external cookbook dependencies, and migrating security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers, with moderate complexity due to SSL certificate management and database configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook versions (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with node attributes for site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and node configuration
- `Vagrantfile`: Development environment provisioning - will need Ansible equivalent for local testing
- `vagrant-provision.sh`: Shell provisioning script - may contain additional setup steps to migrate

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to community.crypto.openssl_* modules for better certificate lifecycle management
- **Firewall Configuration**: UFW firewall rules hardcoded in execute resources - migrate to community.general.ufw module for idempotent firewall management
- **SSH Hardening**: Direct sshd_config file manipulation via sed commands - replace with ansible.posix.sshd_config module for safer SSH configuration
- **Fail2ban Integration**: Template-based jail.local configuration - migrate to community.general.fail2ban module
- **Credential Patterns Identified**:
  - Redis authentication: Hardcoded password 'redis_secure_password_123' in cache cookbook
  - PostgreSQL credentials: Hardcoded database password 'fastapi_password' in fastapi-tutorial cookbook
  - SSL certificate generation: Self-signed certificates with hardcoded subject information
  - Database connection strings: Plaintext credentials in .env file generation

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses a ruby_block to patch Redis configuration files post-installation - this custom logic needs to be replicated using Ansible's lineinfile or replace modules
- **Service Dependencies**: Complex service startup ordering between PostgreSQL, Redis, and application services - requires careful use of Ansible handlers and service dependencies
- **Template Migration**: Multiple ERB templates need conversion to Jinja2 format, particularly nginx.conf.erb and security configuration templates
- **Git Repository Management**: FastAPI application deployment via git clone needs migration to ansible.builtin.git module with proper change detection

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web services)
2. **cache** (low complexity, independent caching services)  
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions

- The target environment will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+)
- Self-signed certificates are acceptable for the target environment (no Let's Encrypt or CA-signed certificate requirements identified)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and the 'main' branch structure is stable
- PostgreSQL will be installed locally rather than using an external database service
- The current hardcoded passwords are acceptable for the target environment or will be externalized to Ansible Vault
- UFW firewall is the preferred firewall solution (no iptables or firewalld requirements identified)
- The nginx sites configuration pattern (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained
- Vagrant-based development workflow will continue to be used (Vagrantfile suggests local development environment)
- The custom Redis configuration patching logic is still required in the target environment
- systemd is available on target systems for service management (based on fastapi-tutorial service file creation)