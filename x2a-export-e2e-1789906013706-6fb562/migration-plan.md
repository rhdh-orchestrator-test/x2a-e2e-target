# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a Python application stack. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning - will need Ansible equivalent for local testing
- `vagrant-provision.sh`: Shell provisioning script - may contain additional setup steps to preserve

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

- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban Integration**: Custom jail configuration for nginx protection - migrate to community.general.fail2ban module
- **SSL Certificate Management**: Self-signed certificate generation per site - migrate to community.crypto.openssl_* modules
- **Sysctl Security Tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module
- **Vault/secrets management**: 
  - Hardcoded credentials identified in cache cookbook (Redis password: 'redis_secure_password_123')
  - Database credentials in fastapi-tutorial cookbook (PostgreSQL password: 'fastapi_password')
  - SSL certificate generation with hardcoded subject information
  - Approximately 3 credential instances requiring Ansible Vault migration

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses ruby_block to modify Redis configuration files post-installation - requires custom Ansible tasks with lineinfile or replace modules
- **Git Repository Management**: FastAPI tutorial clones from GitHub - ensure git module handles repository updates and authentication properly
- **Service Dependencies**: PostgreSQL must be running before database operations - implement proper task ordering with handlers
- **SSL Certificate Automation**: Self-signed certificate generation per site requires loop iteration over site configurations
- **Template Migration**: ERB templates need conversion to Jinja2 format for nginx.conf, security.conf, and fail2ban configurations

### Migration Order

1. **cache** (low risk, high value) - Straightforward service installation with known configuration patterns
2. **nginx-multisite** (moderate complexity) - Complex but well-structured security and SSL configurations
3. **fastapi-tutorial** (high complexity, dependencies) - Requires database setup, application deployment, and service management coordination

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require Let's Encrypt or CA-signed certificates)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- Current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault in production)
- The sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the actual target domain structure
- UFW firewall is the preferred firewall solution for the target environment
- Redis configuration patching via ruby_block represents necessary fixes that should be preserved in Ansible implementation
- The systemd service approach for FastAPI application is preferred over other process management solutions
- Vagrant-based development workflow should be preserved with Ansible provisioning