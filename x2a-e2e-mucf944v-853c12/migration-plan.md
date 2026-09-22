# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a Python FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external cookbook dependencies, and migrating security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers, with moderate complexity due to SSL certificate management, database setup, and security hardening requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via Ruby block, memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external supermarket cookbooks (nginx, memcached, redisio)
- `solo.json`: Chef Solo run list and node attributes configuration with site-specific SSL settings and security policies
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning for testing cookbook functionality
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or custom package/service tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipe files - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled and password authentication disabled via direct file modification - use ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules managed via shell commands - replace with community.general.ufw module
- **Fail2ban Configuration**: Template-based jail configuration - migrate templates to Jinja2 format
- **Database Credentials**: PostgreSQL user creation with embedded passwords - migrate to Ansible Vault for credential management

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a Ruby block that performs complex Redis configuration file manipulation - this will need to be reimplemented using Ansible's lineinfile or replace modules with appropriate regex patterns
- **Git Repository Management**: FastAPI cookbook clones and manages a Git repository with specific revision tracking - ensure ansible.builtin.git module handles the same synchronization behavior
- **Service Dependencies**: Complex service startup ordering between PostgreSQL, Redis, and application services - implement proper handler chains and service dependencies in Ansible
- **Multi-site SSL Configuration**: Dynamic SSL certificate generation for multiple sites requires careful loop implementation in Ansible with proper certificate validation
- **Template Migration**: ERB templates need conversion to Jinja2 format, particularly the nginx.conf and security configuration templates

### Migration Order

1. **cache** (low risk, foundational service) - Start with caching layer as it has fewer dependencies and simpler configuration
2. **nginx-multisite** (moderate complexity) - Migrate web server configuration after caching is stable, includes security hardening
3. **fastapi-tutorial** (high complexity) - Final migration due to application dependencies on database, virtual environment, and service management

### Assumptions

- The target environment will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment, or a proper CA-signed certificate process will be implemented separately
- The PostgreSQL and Redis services will continue to run on the same hosts as the applications (no separation to dedicated database servers)
- The current hardcoded passwords are acceptable for development/testing environments, but production deployments will use Ansible Vault
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and the 'main' branch will be the deployment target
- UFW firewall rules and fail2ban configurations are appropriate for the target security posture
- The systemd service management approach will be maintained in the target environment
- Vagrant-based development workflow will be replaced with molecule or similar Ansible testing framework