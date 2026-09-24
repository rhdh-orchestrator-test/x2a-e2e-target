# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a Python application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, log directory setup, and configuration file manipulation
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, memcached integration, custom Redis configuration fixes via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration

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

- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban Integration**: Custom jail.local configuration - migrate using ansible.builtin.template
- **SSL Certificate Management**: Self-signed certificate generation per site - migrate to community.crypto.openssl_* modules
- **Sysctl Security Tuning**: Custom kernel parameter hardening - migrate to ansible.posix.sysctl
- **Credential Management**: 
  - Redis password hardcoded in recipe (redis_secure_password_123)
  - PostgreSQL credentials hardcoded (fastapi:fastapi_password)
  - Database connection strings in environment files
  - SSL certificate paths and permissions management
  - Approximately 4-5 credential instances requiring Ansible Vault migration

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses ruby_block to manipulate Redis configuration files post-installation - will need equivalent Ansible lineinfile or replace tasks
- **Complex SSL Setup**: Per-site SSL certificate generation with proper file permissions and group ownership requires careful Ansible crypto module usage
- **Service Dependencies**: PostgreSQL must be running before database/user creation, nginx reload dependencies on configuration changes
- **Git Repository Management**: FastAPI tutorial clones from GitHub - ensure idempotent git module usage in Ansible
- **Template Migration**: Multiple ERB templates need conversion to Jinja2 format (nginx.conf.erb, security.conf.erb, site.conf.erb, fail2ban.jail.local.erb, sysctl-security.conf.erb)

### Migration Order

1. **cache** (low risk, high value) - Straightforward service installation and configuration, good starting point
2. **nginx-multisite** (moderate complexity) - Core web infrastructure, security configurations require careful testing
3. **fastapi-tutorial** (high complexity, dependencies) - Application deployment with database dependencies, requires cache and nginx to be functional

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require Let's Encrypt or CA-signed certificates)
- The current hardcoded passwords are acceptable for migration (production should use Ansible Vault)
- The FastAPI tutorial GitHub repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- The sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the actual target hostnames
- UFW firewall is the preferred firewall solution for the target environment
- The ruby_block configuration fixes in the Redis setup are still necessary and will be replicated in Ansible
- Vagrant-based development workflow will be maintained or replaced with molecule for Ansible testing
- The systemd service approach for FastAPI application management is preferred over other process managers