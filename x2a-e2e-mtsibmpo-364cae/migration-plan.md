# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban jail configuration, UFW firewall rules, SSH security hardening, sysctl security parameters

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service setup, Redis with password authentication, custom Redis configuration cleanup via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo configuration with run_list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant environment

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks
- **Chef Supermarket cookbooks**: Convert to equivalent Ansible Galaxy roles or custom tasks

### Security Considerations
- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL password ('fastapi_password') are embedded in recipe code - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths defined in attributes - implement proper certificate deployment with Ansible Vault for private keys
- **SSH security configuration**: Root login disable and password authentication disable via sed commands - convert to ansible.posix.sshd_config module
- **Firewall rules**: UFW commands executed via shell - migrate to community.general.ufw module
- **System security**: sysctl security parameters via template - convert to ansible.posix.sysctl module
- **Credential types per module**:
  - nginx-multisite: SSL certificates and private keys
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables

### Technical Challenges
- **Ruby block configuration fixes**: The cache cookbook uses a ruby_block to manually edit Redis configuration files - requires conversion to Ansible lineinfile or template modules with proper configuration management
- **Multi-site SSL configuration**: Complex nginx virtual host setup with SSL for multiple subdomains requires careful template conversion and certificate management
- **Database initialization**: PostgreSQL user and database creation via shell commands needs conversion to community.postgresql.* modules
- **Service dependencies**: Proper ordering of PostgreSQL, Redis, and nginx services with their dependent applications
- **File permissions and ownership**: Multiple file/directory resources with specific ownership (www-data, redis) need careful mapping to Ansible file module

### Migration Order
1. **cache** (low risk, foundational service) - Redis and memcached setup with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies
3. **nginx-multisite** (high complexity) - Web server with SSL, security hardening, and multiple site configurations

### Assumptions
- SSL certificates are manually managed and placed in /etc/ssl/certs and /etc/ssl/private - certificate provisioning process needs clarification
- The FastAPI tutorial application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Current Chef Solo execution model can be replaced with Ansible playbook execution
- Vagrant development environment will be replaced with equivalent Ansible-based local testing
- Target systems have sudo access for package installation and service management
- Network connectivity allows access to package repositories and Git repositories
- The 'www-data' user exists on target systems for nginx file ownership
- PostgreSQL service can be managed via systemd on target platforms
- UFW firewall is the preferred firewall solution (vs. iptables or firewalld)