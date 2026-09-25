# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation via external cookbook, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration templates

### Security Considerations

- **Hardcoded Credentials**: Multiple hardcoded passwords identified requiring vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL password: `fastapi_password` in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env files
- **SSL Certificate Management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules or Let's Encrypt integration
- **SSH Hardening**: Root login disable and password authentication disable configurations need migration to ansible.posix.sshd_config
- **Firewall Configuration**: UFW rules and fail2ban jail configurations require migration to community.general.ufw and ansible.builtin.template modules
- **File Permissions**: SSL certificate and private key permissions (ssl-cert group, 0710/0640 modes) need careful migration

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook contains a Ruby block that manually edits Redis configuration files to remove specific directives - this complex logic needs conversion to Ansible lineinfile or template modules
- **Multi-Site SSL Management**: Dynamic SSL certificate generation for multiple sites based on node attributes requires Ansible loops and conditional logic
- **Service Dependencies**: PostgreSQL service must be running before database user creation, requiring proper Ansible task ordering and handlers
- **Git Repository Management**: FastAPI application deployment via git clone needs migration to ansible.builtin.git module with proper change detection
- **Python Virtual Environment**: Complex pip installation within virtual environments requires ansible.builtin.pip module with virtualenv parameters

### Migration Order

1. **cache** (moderate complexity, standalone caching services)
2. **nginx-multisite** (high complexity due to SSL and security configurations, but no application dependencies)
3. **fastapi-tutorial** (moderate complexity, depends on database setup but isolated application)

### Assumptions

- Current Chef cookbooks are actively used in production environments
- SSL certificates are currently self-signed for development/testing purposes
- PostgreSQL and Redis services are intended to run on the same hosts as the applications
- UFW firewall and fail2ban are the preferred security tools (Ubuntu-centric approach)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Chef Supermarket cookbooks (nginx, memcached, redisio) provide the expected functionality and their Ansible equivalents will maintain compatibility
- The target environment supports systemd for service management
- Current hardcoded passwords are acceptable for development but will need proper secret management in production
- The multi-site configuration pattern (test.cluster.local, ci.cluster.local, status.cluster.local) represents the actual target domain structure