# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, memcached integration, custom Redis configuration patching, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment setup, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-domain SSL certificates, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef solo configuration with run list and node attributes - contains site configurations, SSL paths, and security settings
- `solo.rb`: Chef solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment setup for testing cookbooks locally
- `vagrant-provision.sh`: Vagrant provisioning script for Chef solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment with local cluster domains (.cluster.local)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules or community.crypto collection
- **Firewall Configuration**: UFW rules migration to community.general.ufw module
- **SSH Hardening**: SSH configuration changes need ansible.builtin.lineinfile or ansible.posix.sshd_config modules
- **Fail2ban Configuration**: Template-based jail configuration requires community.general.fail2ban module
- **Vault/secrets management**: 
  - Hardcoded credentials found in cache cookbook (Redis password: 'redis_secure_password_123')
  - Database credentials in fastapi-tutorial cookbook (PostgreSQL password: 'fastapi_password')
  - SSL certificate paths and configurations in nginx-multisite attributes
  - SSH and security settings stored in node attributes

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook contains a Ruby block that manually edits Redis configuration files - this needs conversion to Ansible template or lineinfile operations
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple domains requires careful Ansible loop and certificate module usage
- **Database Initialization**: PostgreSQL user and database creation with proper privilege management needs postgresql modules
- **Service Dependencies**: Ensuring proper service startup order (PostgreSQL before FastAPI, nginx after SSL certificates)
- **Template Migration**: Converting ERB templates to Jinja2 templates for nginx configuration, fail2ban jails, and security configurations

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached setup with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with SSL and security configurations, no application dependencies
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- The .cluster.local domains suggest this is for internal/development use rather than production internet-facing deployment
- Self-signed certificates are acceptable for the target environment (development/internal use)
- PostgreSQL and Redis passwords can be externalized to Ansible Vault during migration
- The target systems will have similar package availability (Ubuntu/CentOS package managers)
- Systemd is available on target systems for service management
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible during and after migration
- Current Chef solo execution model suggests single-node deployments rather than multi-node orchestration
- UFW firewall is the preferred firewall solution for the target environment
- The existing file structure under /opt/ and /var/www/ is acceptable for the Ansible-managed deployment