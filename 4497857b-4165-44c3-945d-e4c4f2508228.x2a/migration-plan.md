# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to SSL certificate management, security hardening, and database configuration. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis server including authentication, custom log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis authentication (requirepass), memcached integration, Redis log directory management, configuration file manipulation via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package for Redis installation and configuration

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to ansible.builtin.openssl_* modules or community.crypto collection
- **Hardcoded Credentials**: 
  - Redis password 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password 'fastapi_password' in fastapi-tutorial cookbook
  - Database credentials in .env file creation
- **SSH Hardening**: Root login disable and password authentication disable via sshd_config modifications
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH ports
- **Fail2ban Integration**: Jail configuration for intrusion prevention
- **Sysctl Security Tuning**: Kernel parameter hardening via sysctl.d configuration

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses a ruby_block to manipulate Redis configuration files post-installation - requires conversion to Ansible lineinfile or replace modules
- **Service Dependencies**: Complex service ordering between PostgreSQL, nginx, and application services - needs careful Ansible handler and dependency management
- **SSL Certificate Lifecycle**: Self-signed certificate generation with proper file permissions and ownership - migrate to community.crypto.x509_certificate module
- **Multi-site Configuration**: Dynamic site configuration based on node attributes - requires Ansible loops and template generation
- **Database Initialization**: PostgreSQL user and database creation with proper privilege assignment - use community.postgresql collection

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with SSL and security hardening
3. **fastapi-tutorial** (high complexity, dependencies) - Application deployment requiring database, virtual environment, and service integration

### Assumptions

- Target systems will have Python 3 and pip available for FastAPI application deployment
- SSL certificates are self-signed for development purposes - production deployment may require Let's Encrypt or CA-signed certificates
- PostgreSQL service is managed locally on the same host as the FastAPI application
- UFW firewall is the preferred firewall solution (Ubuntu-centric assumption)
- Systemd is available for service management (modern Linux distributions)
- The nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) are for internal/development use based on .local domain usage
- Redis and memcached will run on default ports (6379 and 11211 respectively)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- File ownership patterns (www-data for nginx, redis user for Redis) are consistent across target systems