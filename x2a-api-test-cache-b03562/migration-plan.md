# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI tutorial application with PostgreSQL backend. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and preserving security configurations including fail2ban, UFW firewall, and SSH hardening.

**Migration Complexity**: Medium (3 cookbooks, moderate security configurations, external dependencies)
**Estimated Timeline**: 2-3 weeks for full migration and testing
**Target Environment**: Fedora 42 (based on Vagrantfile), KVM/libvirt virtualization

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW, SSH hardening, and self-signed certificate generation for development
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall rules, SSH security hardening, sysctl security tuning, custom lineinfile resource

- **cache**:
    - Description: Caching services configuration with Redis authentication and Memcached, including Redis configuration workarounds and log directory management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication (redis_secure_password_123), Memcached service, Redis log directory creation, configuration file manipulation via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef node attributes defining nginx sites configuration, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup for Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443)
- `vagrant-provision.sh`: Automated Chef installation and cookbook dependency resolution via Berkshelf

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration, though cookbooks support Ubuntu ≥18.04 and CentOS ≥7.0)
- **Virtual Machine Technology**: KVM/libvirt (configured in Vagrantfile with 2GB RAM, 2 CPUs)
- **Cloud Platform**: Not specified (local development environment)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or manual configuration via templates
- **berkshelf**: Replace with ansible-galaxy for role dependency management
- **chef-solo**: Replace with ansible-playbook execution

### Security Considerations

- **Hardcoded Redis Password**: The cache cookbook contains a hardcoded Redis password ('redis_secure_password_123') that must be moved to Ansible Vault
- **PostgreSQL Credentials**: FastAPI cookbook has hardcoded database credentials ('fastapi_password') requiring Vault migration
- **SSL Certificate Management**: Self-signed certificate generation needs conversion to ansible.builtin.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable configurations need preservation
- **Firewall Rules**: UFW rules for SSH (22), HTTP (80), and HTTPS (443) must be maintained
- **Fail2ban Configuration**: Intrusion prevention settings require template conversion
- **Sysctl Security**: Kernel security parameters need migration to ansible.posix.sysctl module

**Vault/secrets management**: 
- **nginx-multisite**: 0 credentials (uses self-signed certificates)
- **cache**: 1 hardcoded password (Redis authentication)
- **fastapi-tutorial**: 2 hardcoded credentials (PostgreSQL user password, database connection string)

### Technical Challenges

- **Ruby Block Workarounds**: The cache cookbook uses ruby_block to manipulate Redis configuration files, requiring conversion to Ansible lineinfile or template modules
- **Custom Resource Migration**: The nginx-multisite cookbook defines a custom 'lineinfile' resource that needs conversion to ansible.builtin.lineinfile module
- **Berkshelf to Galaxy**: Dependency management migration from Berksfile to requirements.yml
- **Chef Solo to Playbook**: Converting solo.json node attributes to Ansible group_vars or host_vars
- **Template Conversion**: ERB templates need conversion to Jinja2 format
- **Service Notification**: Chef's delayed notifications need conversion to Ansible handlers
- **Git Repository Cloning**: Chef git resource needs conversion to ansible.builtin.git module with proper authentication handling

### Migration Order

1. **cache** (low complexity, minimal dependencies, isolated functionality)
2. **fastapi-tutorial** (moderate complexity, database setup, systemd service management)
3. **nginx-multisite** (high complexity, security configurations, multiple templates, custom resources)

### Assumptions

- The target Fedora 42 environment has package management compatibility with the current Ubuntu/CentOS support in Chef cookbooks
- The FastAPI tutorial GitHub repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- Self-signed certificates are acceptable for the development environment (production would require proper CA-signed certificates)
- The current IP addressing scheme (192.168.121.10) and port forwarding configuration will be maintained
- PostgreSQL and Redis services can be managed via standard systemd on Fedora 42
- The libvirt/KVM virtualization platform supports the required networking configuration
- Chef's ruby_block workarounds for Redis configuration indicate potential compatibility issues that may also affect Ansible deployment
- The custom lineinfile resource functionality can be fully replicated with Ansible's built-in lineinfile module
- External cookbook dependencies (nginx, memcached, redisio) provide functionality that can be replicated with native Ansible modules or community collections
- The current security hardening approach (fail2ban, UFW, SSH configuration) is appropriate for the target Fedora environment
- Database initialization and user creation can be performed with elevated privileges in the Ansible environment
- SSL certificate paths and permissions model will remain compatible across the migration