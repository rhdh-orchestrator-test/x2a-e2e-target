# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a Python FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL termination, fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching infrastructure with memcached and Redis services, including Redis authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (requires assessment for Ansible conversion)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support required based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Multiple credential patterns identified requiring Ansible Vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL credentials: `fastapi_password` in fastapi-tutorial cookbook
  - Database connection strings with embedded passwords in environment files
- **SSL Certificate Management**: Self-signed certificate generation for development environments needs conversion to ansible.builtin.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable configurations need migration to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules and fail2ban jail configurations require migration to community.general.ufw and community.general.fail2ban modules
- **Sysctl Security**: Kernel parameter tuning needs conversion to ansible.posix.sysctl module

### Technical Challenges

- **Multi-Service Orchestration**: The nginx-multisite cookbook manages multiple interdependent services (nginx, fail2ban, UFW, SSL) requiring careful Ansible task ordering and handler coordination
- **Custom Redis Configuration**: The cache cookbook includes a Ruby block hack to modify Redis configuration files post-installation, requiring conversion to Ansible template or lineinfile modules
- **Dynamic Site Generation**: The nginx cookbook dynamically creates virtual hosts based on node attributes, requiring Ansible loops and template generation
- **PostgreSQL Database Initialization**: Database and user creation commands need conversion to community.postgresql.* modules with proper idempotency
- **Systemd Service Management**: Custom systemd service file creation and management requires ansible.builtin.systemd module integration

### Migration Order

1. **cache** (low risk, foundational service) - Standalone caching services with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but isolated functionality  
3. **nginx-multisite** (high complexity, multiple dependencies) - Complex multi-service configuration with security hardening and SSL management

### Assumptions

- **Development Environment Focus**: The presence of Vagrant configuration and self-signed certificates suggests this is primarily a development/testing environment rather than production
- **Ubuntu/Debian Primary Target**: Package management and service names suggest Debian-family systems as the primary target, though CentOS support is declared
- **Local Development Workflow**: The use of Chef Solo rather than Chef Server indicates a local/standalone deployment model that maps well to Ansible
- **Static Site Configuration**: The nginx sites appear to be static configurations rather than dynamically managed applications
- **Network Connectivity**: Git repository cloning assumes internet connectivity for the fastapi-tutorial application deployment
- **Root Access Required**: Several operations (SSL certificate generation, system service management, firewall configuration) assume root privileges
- **File System Permissions**: The cookbooks assume standard Linux file system permissions and user/group structures (www-data, ssl-cert group)