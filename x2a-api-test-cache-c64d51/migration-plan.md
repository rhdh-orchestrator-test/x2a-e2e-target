# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI application with PostgreSQL backend. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates, firewall rules, and hardened SSH settings.

**Migration Complexity**: Medium-High
**Estimated Timeline**: 3-4 weeks
**Team Coordination Required**: DevOps, Security, and Application teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL termination for multiple subdomains (test.cluster.local, ci.cluster.local, status.cluster.local), security hardening with fail2ban and UFW firewall, custom lineinfile resource for configuration management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Self-signed SSL certificate generation, site-specific document roots, security configurations (fail2ban, UFW, SSH hardening), custom ERB templates for nginx.conf and site configurations

- **cache**:
    - Description: Caching services configuration with Memcached and Redis, includes Redis authentication and custom configuration fixes for deprecated Redis directives
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication (redis_secure_password_123), custom Ruby block for Redis config cleanup, Memcached default configuration, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python application deployment with PostgreSQL database, includes Git repository cloning, Python virtual environment setup, systemd service configuration, and database initialization
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: GitHub repository integration (https://github.com/dibanez/fastapi_tutorial.git), PostgreSQL user and database creation, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook references
- `solo.json`: Chef Solo run list configuration and node attributes including site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, network configuration (192.168.121.10), and port forwarding (80→8080, 443→8443)
- `vagrant-provision.sh`: Automated Chef installation and provisioning script with Berkshelf dependency management

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations). Primary target appears to be Ubuntu based on package management commands in recipes.
- **Virtual Machine Technology**: KVM/libvirt (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or private cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks
- **Chef Berkshelf**: Replace with Ansible Galaxy for role dependencies (ansible-galaxy requirements.yml)
- **Chef Solo**: Replace with ansible-playbook execution

### Security Considerations

- **SSL Certificate Management**: Migration approach for self-signed certificate generation using OpenSSL commands, certificate file permissions (640 for private keys), and ssl-cert group management
- **Firewall Configuration**: UFW rules for SSH (22), HTTP (80), and HTTPS (443) ports with default deny policy
- **SSH Hardening**: Root login disabled, password authentication disabled, configuration file modifications via sed commands
- **Fail2ban Integration**: Jail configuration for nginx protection against brute force attacks
- **Vault/secrets management**: 
  - **cache module**: 1 hardcoded Redis password ('redis_secure_password_123') in recipes/default.rb
  - **fastapi-tutorial module**: 2 hardcoded credentials (PostgreSQL user 'fastapi' with password 'fastapi_password', database connection string in .env file)
  - **nginx-multisite module**: SSL certificate subject information hardcoded in ssl.rb recipe
  - **Total credentials detected**: 3 credential sets requiring Ansible Vault migration

### Technical Challenges

- **Custom Chef Resource Migration**: The lineinfile.rb custom resource in nginx-multisite needs conversion to ansible.builtin.lineinfile module with equivalent functionality
- **Ruby Block Logic**: Complex Ruby blocks in cache cookbook for Redis configuration cleanup require conversion to Ansible tasks with conditional logic
- **Template Variable Mapping**: ERB templates (.erb files) need conversion to Jinja2 templates (.j2) with variable syntax changes (node['attr'] → ansible_facts or vars)
- **Service Notification Patterns**: Chef's notifies pattern needs conversion to Ansible handlers with proper trigger conditions
- **Git Repository Integration**: Chef git resource needs conversion to ansible.builtin.git module with equivalent revision and sync behavior
- **PostgreSQL Database Initialization**: Complex shell commands for database and user creation need conversion to community.postgresql.* modules

### Migration Order

1. **cache** (Priority 1: Low risk, standalone caching services, minimal external dependencies)
2. **nginx-multisite** (Priority 2: Moderate complexity due to custom resource and multiple templates, but well-isolated functionality)
3. **fastapi-tutorial** (Priority 3: High complexity due to application deployment, database integration, and systemd service management)

### Assumptions

- The target environment will maintain the same OS family (Ubuntu/Debian-based) as indicated by apt-get commands in vagrant-provision.sh
- SSL certificates will continue to be self-signed for development environments, but production deployment may require Let's Encrypt or CA-signed certificates
- The Vagrant development environment will be replaced with an equivalent Ansible testing setup using molecule or similar tools
- Network configuration (192.168.121.10 IP address) and port forwarding requirements will remain consistent
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and the main branch will be stable
- PostgreSQL version compatibility will be maintained between Chef and Ansible deployments
- Redis and Memcached service configurations will maintain backward compatibility
- The custom lineinfile resource functionality is adequately covered by Ansible's built-in lineinfile module
- Security hardening requirements (fail2ban, UFW, SSH configuration) will remain consistent with current implementation
- Systemd service management approach will be preserved in the Ansible migration
- File and directory ownership/permissions patterns will be maintained (www-data for web content, ssl-cert group for certificates)
- The Chef Solo execution model will be replaced with standard Ansible playbook execution without requiring Ansible Tower/AWX