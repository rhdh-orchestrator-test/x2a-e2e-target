# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached integration, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban/UFW, and SSH configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration for all three cookbooks
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management
- **Chef Solo**: Replace with ansible-playbook execution model

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - maintain these security settings
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - preserve firewall rules in Ansible
- **Fail2ban Integration**: SSH protection via fail2ban - maintain jail configurations
- **Sysctl Security Tuning**: Kernel parameter hardening - preserve security configurations

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need custom Ansible lineinfile tasks or template management
- **Multi-site SSL Certificate Generation**: Dynamic certificate generation for multiple sites based on node attributes - requires Ansible loops and conditional certificate creation
- **PostgreSQL Database Initialization**: Database and user creation with proper privilege assignment - use community.postgresql collection
- **Systemd Service Management**: Custom systemd service file creation and management for FastAPI application - use ansible.builtin.systemd module
- **Git Repository Integration**: FastAPI application deployment from Git repository - use ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, foundational service)
   - Straightforward package installation and service management
   - Redis configuration complexity is isolated and well-defined
   
2. **nginx-multisite** (moderate complexity, security-critical)
   - Complex multi-site configuration with SSL
   - Security hardening affects entire system
   - Dependencies on SSL certificate generation
   
3. **fastapi-tutorial** (high complexity, application-specific)
   - Application deployment with multiple dependencies
   - Database integration and service management
   - Depends on system being properly secured

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in Chef metadata
- Self-signed certificates are acceptable for development/testing environments (production may require proper CA-signed certificates)
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without changing the actual credential values
- The FastAPI tutorial Git repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- Current Chef Solo execution model can be replaced with standard Ansible playbook execution
- UFW firewall is the preferred firewall solution (vs. iptables or firewalld)
- The custom Redis configuration patching in the cache cookbook is still necessary and cannot be replaced with standard Redis configuration management
- Development environment will continue to use Vagrant, but Ansible provisioning will replace Chef Solo
- SSL certificate paths (/etc/ssl/certs and /etc/ssl/private) are standard and acceptable for the target environment
- The nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the actual target domain structure