# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to SSL certificate management, security hardening, and database configuration. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv setup, PostgreSQL database and user creation, systemd service management, environment file configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL certificates, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to ansible.builtin.openssl_* modules
- **Hardcoded Credentials**: 
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL credentials: `fastapi:fastapi_password` in fastapi-tutorial cookbook
  - Database connection strings in environment files
- **SSH Hardening**: Root login disable and password authentication disable via sshd_config modifications
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH ports
- **Fail2ban Integration**: Custom jail.local configuration for intrusion prevention
- **Sysctl Security Tuning**: Kernel parameter hardening via sysctl.d configuration

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains custom Ruby code for Redis configuration file manipulation that needs conversion to Ansible lineinfile or template tasks
- **Multi-Site SSL**: Complex SSL certificate generation and management for multiple domains requires careful Ansible loop implementation
- **Service Dependencies**: PostgreSQL must be configured before FastAPI application deployment, requiring proper task ordering
- **File Permissions**: SSL certificate files have specific ownership (root:ssl-cert) and permissions (640/710) that must be preserved
- **Template Migration**: ERB templates need conversion to Jinja2 format for nginx.conf, security.conf, and fail2ban configurations

### Migration Order

1. **cache** (low risk, foundational service) - Redis and memcached are standalone services with minimal dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, requires coordination with nginx for reverse proxy setup

### Assumptions

- SSL certificates are self-signed for development/testing environments - production deployment may require Let's Encrypt or CA-signed certificates
- PostgreSQL database is local to the application server - no external database cluster configuration visible
- UFW firewall rules are sufficient for the security model - no advanced iptables or network security groups configured
- Chef Solo execution model suggests single-node deployment - clustering or multi-node coordination not addressed
- Git repository access for FastAPI tutorial assumes public GitHub access - private repositories may require SSH key or token configuration
- System package managers (apt/yum) are available and configured - no custom package repositories or offline installation requirements visible
- Service user accounts (www-data, redis, postgres) exist or are created by package installation - no custom user provisioning logic observed