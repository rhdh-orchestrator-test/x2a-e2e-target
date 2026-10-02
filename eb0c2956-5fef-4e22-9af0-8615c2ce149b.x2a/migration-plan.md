# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH security hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found requiring Ansible Vault migration:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env files
- **SSH Security**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Integration**: Custom jail.local template - migrate to community.general.fail2ban module
- **SSL Certificate Management**: Certificate and private key path configurations need secure handling in Ansible

### Technical Challenges

- **Ruby Block Workarounds**: The cache cookbook contains a ruby_block hack to fix Redis configuration by removing specific lines - this needs to be replaced with proper Ansible template or lineinfile modules
- **Git Repository Cloning**: FastAPI cookbook clones from GitHub - ensure Ansible git module handles authentication and updates properly
- **Service Dependencies**: PostgreSQL must be running before FastAPI application starts - implement proper Ansible handlers and service ordering
- **Multi-site SSL Configuration**: Complex nginx site configuration with SSL requires careful template migration and certificate management
- **Environment File Generation**: .env file creation with database URLs needs secure credential injection

### Migration Order

1. **cache** (moderate complexity, standalone caching services)
2. **nginx-multisite** (high complexity due to security configurations and SSL, but no external service dependencies)
3. **fastapi-tutorial** (highest complexity due to database dependencies, git operations, and service orchestration)

### Assumptions

- SSL certificates are manually managed and placed in standard paths (/etc/ssl/certs, /etc/ssl/private)
- The FastAPI tutorial repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- PostgreSQL installation uses distribution packages rather than custom compilation
- The target environment has internet access for package installation and git cloning
- UFW is the preferred firewall solution (rather than iptables or firewalld)
- The Redis configuration "hack" in the cache cookbook indicates potential compatibility issues with the redisio cookbook that may require custom Redis setup in Ansible
- Site-specific HTML files (test, ci, status) are static content that can be deployed via Ansible copy/template modules
- The current Chef Solo deployment model suggests single-node deployments rather than multi-node orchestration