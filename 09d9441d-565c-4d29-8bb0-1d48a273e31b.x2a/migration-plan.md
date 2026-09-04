# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure setup for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates and firewall rules. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **cache**:
    - Description: Caching services configuration with memcached and Redis authentication, includes custom Redis configuration fixes and log directory management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication (redis_secure_password_123), memcached integration, custom Redis config file manipulation, log directory creation

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, custom lineinfile resource

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef node configuration with site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider
- `vagrant-provision.sh`: Automated Chef installation and cookbook dependency resolution script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for Ansible migration.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **berkshelf**: Replace with ansible-galaxy for role dependency management
- **chef-solo**: Replace with ansible-playbook execution

### Security Considerations

- **SSL Certificate Management**: Migration approach for self-signed certificate generation using OpenSSL commands
  - Current: OpenSSL command execution in Chef recipes
  - Target: community.crypto.openssl_* Ansible modules for certificate generation
- **Firewall Configuration**: UFW rules migration to firewalld or iptables
  - Current: UFW command execution for SSH, HTTP, HTTPS ports
  - Target: ansible.posix.firewalld or community.general.ufw modules
- **SSH Hardening**: Configuration file modifications for root login and password authentication
  - Current: sed command execution for sshd_config modifications
  - Target: ansible.builtin.lineinfile module for SSH configuration
- **Vault/secrets management**: For each module, credential patterns identified:
  - **cache module**: 1 hardcoded Redis password (redis_secure_password_123) in recipes/default.rb
  - **fastapi-tutorial module**: 2 hardcoded credentials (PostgreSQL user password 'fastapi_password' and database connection string) in recipes/default.rb and .env file
  - **nginx-multisite module**: SSL certificate subject information hardcoded in recipes/ssl.rb
  - **Total**: 4 credential instances requiring Ansible Vault migration

### Technical Challenges

- **Custom Ruby Resource Migration**: The nginx-multisite cookbook contains a custom lineinfile resource (resources/lineinfile.rb) that needs conversion to Ansible's built-in lineinfile module
- **Redis Configuration Hacks**: The cache cookbook contains Ruby block code that manually manipulates Redis configuration files, requiring careful translation to Ansible tasks
- **Template File Migration**: Multiple ERB templates need conversion to Jinja2 format (nginx.conf.erb, site.conf.erb, fail2ban.jail.local.erb, security.conf.erb, sysctl-security.conf.erb)
- **File Resource Management**: Static files in cookbooks/nginx-multisite/files/default/ (ci/, status/, test/ directories) need migration to Ansible file management
- **Service Dependency Management**: Complex service restart notifications and dependencies need careful mapping to Ansible handlers
- **Git Repository Integration**: FastAPI tutorial cookbook clones from GitHub repository, requiring ansible.builtin.git module configuration

### Migration Order

1. **cache module** (low risk, moderate complexity) - Standalone caching services with clear external dependencies
2. **fastapi-tutorial module** (moderate complexity) - Self-contained application with database dependencies
3. **nginx-multisite module** (high complexity, multiple dependencies) - Complex multi-site configuration with security hardening and custom resources

### Assumptions

- The target environment will maintain the same network configuration (192.168.121.10 private network)
- Self-signed certificates are acceptable for the target environment (no Let's Encrypt or CA integration required)
- The same site names (test.cluster.local, ci.cluster.local, status.cluster.local) will be used in the Ansible deployment
- PostgreSQL and Redis authentication credentials can be migrated to Ansible Vault
- The FastAPI tutorial GitHub repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible
- Ubuntu/CentOS package names and service management will translate directly to RHEL 9
- The libvirt/KVM virtualization platform will be maintained in the target environment
- Berkshelf cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with native Ansible modules
- The custom lineinfile resource behavior can be fully replicated with Ansible's lineinfile module
- Ruby block code for Redis configuration manipulation can be converted to equivalent Ansible tasks
- ERB template variables and logic can be successfully converted to Jinja2 syntax
- File permissions and ownership requirements will remain consistent across Chef and Ansible deployments
- Service restart and reload notifications can be mapped to Ansible handlers without functionality loss
- The development workflow using Vagrant will be maintained or replaced with equivalent Ansible testing methodology