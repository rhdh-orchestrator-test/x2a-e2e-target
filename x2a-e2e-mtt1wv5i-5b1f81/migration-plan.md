# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation via external cookbook, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration with self-signed certificates, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx, memcached, redisio) and local cookbook paths
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or development environment focused

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or custom Ansible tasks for memcached installation and configuration
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom Redis configuration templates

### Security Considerations

- **Hardcoded Credentials**: Multiple hardcoded passwords found requiring vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL password: `fastapi_password` in fastapi-tutorial cookbook
  - Database credentials in environment files
- **SSL Certificate Management**: Self-signed certificate generation needs migration to Ansible crypto modules or Let's Encrypt integration
- **SSH Hardening**: Root login disable and password authentication disable configurations need careful migration
- **Firewall Configuration**: UFW rules and fail2ban jail configurations require community.general.ufw and ansible.builtin.fail2ban modules
- **System Security**: Sysctl security parameters in templates need migration to ansible.posix.sysctl module

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook contains a Ruby block that manually edits Redis configuration files to remove specific lines - this complex logic needs reimplementation in Ansible
- **Multi-Site SSL Management**: Dynamic SSL certificate generation for multiple sites requires careful loop handling in Ansible
- **Service Dependencies**: PostgreSQL service must be running before database user creation, requiring proper Ansible task ordering
- **File Permissions**: Complex SSL certificate permissions (ssl-cert group) need proper Ansible file module configuration
- **Template Migration**: ERB templates need conversion to Jinja2 format with variable mapping

### Migration Order

1. **cache** (moderate complexity, standalone service)
2. **nginx-multisite** (high complexity due to SSL and security features, but no external service dependencies)
3. **fastapi-tutorial** (highest complexity due to application deployment, database setup, and service management)

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require Let's Encrypt or CA-signed certificates)
- The Redis configuration patching hack in the cache cookbook is still necessary in the target environment
- PostgreSQL will be installed locally rather than using an external database service
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible
- UFW and fail2ban are the preferred security tools for the target environment
- Systemd is available for service management on target systems
- The ssl-cert group exists or can be created on target systems for SSL key file permissions