# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached integration, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with site-specific nginx configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

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

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate using ansible.posix.sysctl and lineinfile modules
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate using community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate using template module with Ansible Vault for sensitive configurations
- **Database Credentials**: PostgreSQL user creation with embedded passwords - migrate to Ansible Vault with postgresql_* modules

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or replace modules with proper regex patterns
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple sites based on node attributes - will require Ansible loops and conditional logic
- **Service Dependencies**: Complex service restart notifications and dependencies between nginx, fail2ban, and SSL certificate generation - requires careful Ansible handler design
- **Git Repository Integration**: FastAPI application deployment from Git with virtual environment management - needs integration with ansible.builtin.git and pip modules

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but isolated from web tier
3. **nginx-multisite** (high complexity, multiple dependencies) - Complex multi-site configuration with SSL, security hardening, and firewall rules

### Assumptions

- Target environments will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production deployments may require CA-signed certificates)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible during migration
- Current hardcoded passwords are acceptable for development but will need proper secret management for production
- UFW firewall is the preferred firewall solution (rather than iptables or firewalld)
- The three configured sites (test.cluster.local, ci.cluster.local, status.cluster.local) represent the complete site inventory
- PostgreSQL will continue to be the database backend for the FastAPI application
- Systemd is available on target systems for service management
- The Ruby-based Redis configuration patching represents a temporary workaround that can be replaced with proper configuration management