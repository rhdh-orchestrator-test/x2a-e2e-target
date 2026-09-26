# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis authentication, includes Redis log directory setup and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached integration, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban and UFW firewall, SSH configuration lockdown
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH security hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Security Configuration**: Root login disabled, password authentication disabled - preserve these security settings
- **Firewall Rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS) - migrate to ansible.posix.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate template to Jinja2 format
- **Sysctl Security Tuning**: Custom kernel parameter hardening - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need custom Ansible lineinfile tasks or template replacement
- **Multi-site SSL Certificate Generation**: Dynamic certificate generation for multiple sites based on node attributes - will require Ansible loops and conditional certificate creation
- **PostgreSQL Database Initialization**: Database and user creation with privilege grants - migrate to community.postgresql.* modules
- **Systemd Service Management**: Custom service file creation and daemon-reload handling - use ansible.builtin.systemd and template modules
- **Git Repository Management**: FastAPI application deployment from Git with specific revision tracking - use ansible.builtin.git module

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational infrastructure)
2. **cache** (low-medium complexity, independent caching services)  
3. **fastapi-tutorial** (medium complexity, depends on database and web infrastructure)

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in Chef metadata
- Self-signed certificates are acceptable for development; production may require proper CA-signed certificates or Let's Encrypt integration
- PostgreSQL service is available on target systems or will be installed separately
- Git repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- Current hardcoded passwords are development/testing credentials and will be replaced with proper secrets management
- UFW firewall is the preferred firewall solution (vs. iptables or firewalld)
- The Ruby-based Redis configuration patching indicates potential compatibility issues with the redisio cookbook that may not exist in native Redis installations
- Vagrant development workflow will be replaced with Ansible-based local testing or molecule framework
- The /opt/server vs /var/www document root discrepancy between attributes and solo.json indicates configuration drift that needs resolution