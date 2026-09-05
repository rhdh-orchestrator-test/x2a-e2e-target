# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI tutorial application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates, database credentials, and firewall rules.

**Migration Complexity**: Medium (3 cookbooks, external dependencies, security configurations)
**Estimated Timeline**: 2-3 weeks for complete migration and testing
**Team Coordination**: Requires coordination between web infrastructure, security, and application teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL termination for multiple subdomains (test.cluster.local, ci.cluster.local, status.cluster.local), security hardening with fail2ban and UFW firewall, custom resource for line-in-file operations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Self-signed SSL certificate generation, site-specific document roots, security configurations (fail2ban, UFW, SSH hardening), sysctl security tuning, custom lineinfile resource

- **cache**:
    - Description: Caching services configuration with Memcached and Redis, includes Redis authentication and custom configuration fixes for deprecated directives
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication (redis_secure_password_123), custom Redis configuration cleanup, Memcached service, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook references
- `solo.json`: Chef Solo run list and node attributes including nginx site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, network configuration for testing
- `vagrant-provision.sh`: Automated Chef installation and provisioning script with Berkshelf dependency management

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for Ansible migration.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or manual configuration with ansible.builtin.template
- **Chef Solo**: Replace with Ansible playbooks and inventory management
- **Berkshelf**: Replace with Ansible Galaxy for role dependencies (ansible-galaxy install)

### Security Considerations

- **SSL Certificate Management**: Migration approach for self-signed certificate generation using openssl commands in Ansible tasks
- **Database Credentials**: Hardcoded PostgreSQL password (fastapi_password) and Redis password (redis_secure_password_123) need to be moved to Ansible Vault
- **SSH Security Configuration**: SSH root login disable and password authentication disable need equivalent Ansible configurations
- **Firewall Rules**: UFW firewall rules (SSH, HTTP, HTTPS) need migration to ansible.posix.ufw module
- **Vault/secrets management**: 
  - **cache module**: 1 Redis password credential detected in recipes/default.rb
  - **fastapi-tutorial module**: 2 credentials detected - PostgreSQL user password and database connection string in recipes/default.rb
  - **nginx-multisite module**: SSL certificate paths and self-signed certificate generation, no hardcoded credentials
  - **Total**: 3 credentials requiring Ansible Vault migration

### Technical Challenges

- **Custom Chef Resource**: The nginx-multisite cookbook contains a custom `lineinfile` resource that needs to be replaced with ansible.builtin.lineinfile module
- **Redis Configuration Cleanup**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove deprecated directives - this logic needs to be replicated in Ansible
- **Template Migration**: Multiple ERB templates need conversion to Jinja2 format (nginx.conf.erb, site.conf.erb, security.conf.erb, fail2ban.jail.local.erb, sysctl-security.conf.erb)
- **Git Repository Cloning**: FastAPI tutorial uses Chef's git resource which needs migration to ansible.builtin.git module
- **Systemd Service Management**: Custom systemd service file creation and management needs equivalent Ansible tasks
- **File Permissions and Ownership**: Complex file permission management (ssl-cert group, www-data ownership) requires careful Ansible task ordering

### Migration Order

1. **cache module** (low risk, high value) - Simple service configuration with clear dependencies
2. **fastapi-tutorial module** (moderate complexity) - Application deployment with database setup but straightforward logic
3. **nginx-multisite module** (high complexity, dependencies) - Complex security configurations, custom resources, and multiple templates requiring careful migration

### Assumptions

- The target environment will use the same operating system family (Debian/Ubuntu or RHEL/CentOS) as specified in cookbook metadata
- SSL certificates will continue to be self-signed for development environments, but production may require Let's Encrypt or CA-signed certificates
- The FastAPI tutorial application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Network configuration (192.168.121.10, port forwarding) will be handled outside of Ansible or adapted to target environment
- PostgreSQL and Redis services will be managed by Ansible rather than external package managers
- The ssl-cert group and www-data user exist or will be created in the target environment
- Vagrant-specific configurations will be replaced with appropriate inventory and host management for target deployment method
- Chef Solo's local cookbook execution model will be replaced with Ansible's push-based execution model
- Berkshelf dependency resolution will be replaced with Ansible Galaxy role dependencies where equivalent roles exist
- The current hardcoded passwords are acceptable for development but will need proper secret management for production environments