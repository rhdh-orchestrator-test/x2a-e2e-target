# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and implementing security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site-specific settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration with community.crypto collection
- **SSH hardening**: Root login disabled, password authentication disabled - implement with ansible.posix.sysctl and lineinfile modules
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban integration**: Custom jail configuration - use community.general.fail2ban module
- **Database credentials**: PostgreSQL user and database creation with embedded passwords - secure with Ansible Vault

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis configuration files post-installation - replace with Ansible template or lineinfile modules for cleaner configuration management
- **Multi-site SSL certificate generation**: Dynamic certificate creation per site requires loop-based certificate generation in Ansible using community.crypto.openssl_* modules
- **Service dependency management**: PostgreSQL must be running before FastAPI application starts - implement with Ansible handlers and service dependencies
- **Git repository synchronization**: Chef git resource behavior needs replication with ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, standalone caching services with clear dependencies)
2. **nginx-multisite** (moderate complexity, security configurations require careful testing)
3. **fastapi-tutorial** (high complexity, database dependencies and application deployment)

### Assumptions

- Target environments have internet access for package installation and git repository cloning
- SSL certificates are acceptable as self-signed for development/testing environments
- PostgreSQL and Redis services can be restarted during deployment without data loss concerns
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Current Chef Solo execution model can be replaced with Ansible playbook execution
- UFW firewall rules are appropriate for the target network environment
- Fail2ban configuration is suitable for the expected traffic patterns and security requirements