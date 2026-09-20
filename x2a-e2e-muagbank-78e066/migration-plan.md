# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching services, a FastAPI application, and an nginx reverse proxy with SSL termination. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external dependencies from Chef Supermarket
- `solo.json`: Chef Solo run list and node attributes configuration with site-specific overrides
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Redis configuration tasks
- **nginx (~> 12.0)**: Replace with community.general.nginx_* modules or ansible.builtin.template for configuration

### Security Considerations

- **Hardcoded credentials**: Redis password (`redis_secure_password_123`) and PostgreSQL password (`fastapi_password`) are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificates referenced in nginx configuration need secure deployment mechanism
- **SSH hardening**: Root login disable and password authentication disable configurations need careful migration
- **Firewall rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS) requires ufw module or firewalld equivalent
- **Fail2ban configuration**: Custom jail.local template needs migration to Ansible template module
- **Sysctl security tuning**: Security-focused kernel parameter tuning requires sysctl module

### Technical Challenges

- **Redis configuration patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this hack needs to be replaced with proper Ansible template management
- **PostgreSQL database initialization**: Database and user creation commands use shell execution with conditional logic that needs conversion to postgresql_* modules
- **Multi-site nginx configuration**: Dynamic site configuration based on node attributes requires Ansible loops and template generation
- **Service dependency management**: Proper service ordering (PostgreSQL before FastAPI, nginx after SSL setup) needs explicit Ansible handlers and dependencies
- **File ownership and permissions**: Consistent www-data user/group management across multiple directories and files

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL certificate deployment strategy
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, Git integration, and service management

### Assumptions

- SSL certificates are manually deployed or managed outside of this configuration (no certificate generation or Let's Encrypt integration found)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Target systems have internet access for package installation and Git repository cloning
- The current Chef Solo deployment model will be replaced with Ansible playbook execution
- Database passwords and Redis authentication will be migrated to Ansible Vault for security
- The three virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) represent the actual target domain structure
- UFW firewall is the preferred firewall solution (vs. firewalld on RHEL systems)
- The Ruby-based configuration patching in the Redis setup indicates potential configuration conflicts that need investigation
- Vagrant development environment setup suggests this is a development/testing infrastructure rather than production