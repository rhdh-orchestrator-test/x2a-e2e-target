# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis 6379 with authentication, custom log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication (redis_secure_password_123), memcached integration, Redis log directory management, configuration file manipulation via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test/ci/status.cluster.local), SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Vagrant provisioning script for development setup

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

- **Hardcoded Credentials**: Redis password 'redis_secure_password_123' and PostgreSQL password 'fastapi_password' are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate to community.general.fail2ban module
- **Database Credentials**: PostgreSQL user and database creation with embedded passwords - migrate to Ansible Vault with community.postgresql.* modules

### Technical Challenges

- **Ruby Block Logic**: The Redis configuration patching via ruby_block requires conversion to Ansible lineinfile or replace modules with proper regex patterns
- **Template Dependencies**: ERB templates (.erb files) need conversion to Jinja2 templates with equivalent logic
- **Service Dependencies**: Complex service restart notifications and dependency chains need careful ordering in Ansible tasks
- **Git Repository Management**: FastAPI tutorial git cloning and virtual environment setup requires idempotent task design
- **SSL Certificate Generation**: OpenSSL command execution needs conversion to Ansible crypto modules for better certificate lifecycle management

### Migration Order

1. **cache cookbook** (low risk, isolated caching services)
2. **fastapi-tutorial cookbook** (moderate complexity, database and application setup)
3. **nginx-multisite cookbook** (high complexity, security configurations and SSL management)

### Assumptions

- Target systems will maintain the same OS family (Ubuntu/CentOS) as specified in cookbook metadata
- SSL certificates can remain self-signed for development environments, or external certificate management will be implemented
- Database passwords and Redis authentication will be migrated to Ansible Vault rather than remaining hardcoded
- The three-site configuration (test/ci/status.cluster.local) represents the complete scope of nginx virtual hosts
- UFW firewall is the preferred firewall solution and will be retained in the Ansible implementation
- PostgreSQL and Redis services will continue to run on the same hosts as the applications
- The Chef Solo execution model will be replaced with Ansible playbook execution against inventory hosts
- Development environment provisioning via Vagrant will be replaced with Ansible-based VM configuration
- External cookbook dependencies from Chef Supermarket have equivalent Ansible Galaxy collections or can be implemented with built-in modules