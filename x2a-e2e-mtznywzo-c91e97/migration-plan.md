# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external cookbook dependencies, and migrating security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers, with moderate complexity due to SSL certificate management, database configurations, and security hardening requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban and UFW, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run_list and node attributes - contains site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning with Chef Solo
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence for development)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, custom Redis configuration templates, and service management

### Security Considerations
- SSH hardening configurations: Migrate PermitRootLogin and PasswordAuthentication settings using ansible.posix.sysctl and lineinfile modules
- UFW firewall rules: Convert to ansible.posix.firewalld or ufw module equivalents for port management (SSH, HTTP, HTTPS)
- Fail2ban configuration: Migrate jail.local template to Ansible template module with fail2ban service management
- SSL certificate management: For each site (test.cluster.local, ci.cluster.local, status.cluster.local), migrate self-signed certificate generation using ansible.builtin.openssl_* modules
- Sysctl security tuning: Convert sysctl-security.conf template to ansible.posix.sysctl module
- Credential patterns identified:
  - Redis authentication password (hardcoded in cache cookbook: 'redis_secure_password_123')
  - PostgreSQL database credentials (hardcoded in fastapi-tutorial: 'fastapi_password')
  - SSL certificate paths and permissions management

### Technical Challenges
- Ruby block configuration patching: The cache cookbook uses a ruby_block to modify Redis configuration files post-installation - requires conversion to Ansible lineinfile or replace modules with proper regex patterns
- Multi-site SSL certificate generation: Complex OpenSSL certificate generation for multiple domains needs conversion to ansible.builtin.openssl_certificate and ansible.builtin.openssl_privatekey modules
- PostgreSQL database initialization: Chef's execute resources for database/user creation need conversion to ansible.builtin.postgresql_* modules with proper idempotency
- Systemd service file management: Convert Chef file resources to Ansible template module with systemd daemon-reload handlers

### Migration Order
1. **cache** (low risk, high value) - Straightforward package installation and service management, good starting point
2. **nginx-multisite** (moderate complexity) - More complex due to SSL certificates and security configurations, but well-defined scope
3. **fastapi-tutorial** (high complexity, dependencies) - Most complex due to application deployment, database setup, and service dependencies

### Assumptions
- SSL certificates are self-signed for development/testing environments - production deployment may require Let's Encrypt or CA-signed certificates
- PostgreSQL and Redis passwords are acceptable to remain in plaintext during initial migration - should be moved to Ansible Vault in production
- Target systems have internet access for package installation and Git repository cloning
- UFW firewall is the preferred firewall solution (vs. firewalld on RHEL systems)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- Current Chef Solo deployment model will be replaced with Ansible playbook execution
- Site document root paths may need adjustment between Chef attributes (/opt/server/*) and solo.json configuration (/var/www/*)
- System user 'www-data' exists on target systems for nginx file ownership