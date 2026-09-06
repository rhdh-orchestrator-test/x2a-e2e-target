# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates, firewall rules, and hardened SSH settings. Estimated timeline: 2-3 weeks for a team of 2-3 engineers with moderate Chef/Ansible experience.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **cache**:
    - Description: Caching services configuration with memcached and Redis server setup, including Redis authentication, custom log directory creation, and configuration file patching for compatibility
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom log directory (/var/log/redis), configuration file manipulation via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, systemd service management, and database user provisioning
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment creation, PostgreSQL database and user setup, systemd service configuration, environment file management

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, SSH configuration hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security parameters

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes including site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration specifying cookbook paths, cache location, and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, network configuration (192.168.121.10), and port forwarding (80→8080, 443→8443)
- `vagrant-provision.sh`: Automated Chef installation and cookbook dependency resolution using Berkshelf, with Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for Ansible migration.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or local development environment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Replace with community.crypto.openssl_* modules for certificate generation

### Security Considerations
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands need migration to community.crypto.x509_certificate module with proper key management
- **Firewall Configuration**: UFW rules (SSH, HTTP, HTTPS) need migration to community.general.ufw module
- **SSH Hardening**: Root login disable and password authentication disable need migration to ansible.posix.lineinfile module
- **Fail2ban Configuration**: Custom jail.local template needs migration to ansible.builtin.template module
- **Vault/secrets management**: 
  - **cache module**: 1 hardcoded Redis password (redis_secure_password_123) in recipes/default.rb
  - **fastapi-tutorial module**: 2 hardcoded credentials (PostgreSQL user 'fastapi' with password 'fastapi_password') in recipes/default.rb and .env file
  - **nginx-multisite module**: SSL certificate subject information hardcoded in recipes/ssl.rb
  - Total: 3 credential instances requiring Ansible Vault migration

### Technical Challenges
- **Ruby Block Logic**: The cache cookbook contains complex Ruby code for Redis configuration file manipulation that needs conversion to Ansible lineinfile or replace modules
- **Custom Resource**: nginx-multisite cookbook includes a custom lineinfile resource (resources/lineinfile.rb) that needs migration to ansible.builtin.lineinfile module
- **Template Dependencies**: Multiple ERB templates need conversion to Jinja2 format with variable mapping
- **Service Dependencies**: Complex service restart notifications and dependency chains need careful ordering in Ansible playbooks
- **Git Repository Cloning**: FastAPI tutorial uses git resource with specific revision handling that needs migration to ansible.builtin.git module

### Migration Order
1. **cache** (low risk, standalone caching services with clear external dependencies)
2. **fastapi-tutorial** (moderate complexity, database setup and application deployment)
3. **nginx-multisite** (high complexity, multiple security configurations, custom resources, and template dependencies)

### Assumptions
- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- External cookbook dependencies (nginx, memcached, redisio) are available as equivalent Ansible modules or can be replaced with native package management
- The Vagrant development environment will be replaced with an equivalent Ansible testing setup
- SSL certificate requirements will remain self-signed for development environments
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained in the Ansible version
- PostgreSQL and Redis authentication mechanisms will remain compatible with the existing application requirements
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and compatible
- Systemd service management is available on target systems for the FastAPI application
- The custom Ruby block logic for Redis configuration can be adequately replaced with Ansible's text manipulation modules
- Network configuration and port forwarding requirements will be handled outside of the Ansible playbooks (infrastructure layer)