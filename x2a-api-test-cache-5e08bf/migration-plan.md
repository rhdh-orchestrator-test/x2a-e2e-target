# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates and hardcoded credentials.

**Migration Scope**: 3 Chef cookbooks, 5 external dependencies, SSL certificate management, database credentials, and security hardening configurations.

**Estimated Timeline**: 2-3 weeks for a team of 2-3 engineers, including testing and validation.

**Complexity Level**: Medium - involves multiple services, SSL management, and credential handling.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **cache**:
    - Description: Caching services configuration with memcached and Redis, including authentication setup and custom Redis configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication (redis_secure_password_123), memcached service, custom Redis config file manipulation, log directory creation

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file with database credentials

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL sites (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban integration, UFW firewall, SSH hardening, self-signed SSL certificates, custom lineinfile resource

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef node attributes defining site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider
- `vagrant-provision.sh`: Automated Chef installation and cookbook dependency resolution script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations). Default to Red Hat Enterprise Linux 9 for Ansible migration.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Berkshelf**: Replace with Ansible Galaxy for role dependency management
- **Chef Solo**: Replace with ansible-playbook execution

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation for 3 domains (test.cluster.local, ci.cluster.local, status.cluster.local) using OpenSSL commands - migrate to community.crypto.openssl_* modules
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.lineinfile or community.general.ssh_config modules
- **Fail2ban Integration**: Jail configuration for nginx protection - migrate to community.general.ini_file module
- **Vault/secrets management**: 
  - **cache module**: 1 hardcoded Redis password ('redis_secure_password_123') in recipes/default.rb
  - **fastapi-tutorial module**: 2 hardcoded credentials (PostgreSQL user 'fastapi' with password 'fastapi_password', database connection string in .env file)
  - **nginx-multisite module**: SSL certificate subject information hardcoded in SSL generation command
  - **Total**: 3 credential instances requiring Ansible Vault integration

### Technical Challenges

- **Custom Redis Configuration Manipulation**: The cache cookbook uses a Ruby block to modify Redis config file by removing specific lines - requires custom Ansible lineinfile tasks or template replacement
- **Complex Site Configuration Loop**: nginx-multisite iterates over multiple sites with SSL certificates - requires Ansible loops with conditional SSL certificate generation
- **Custom Chef Resource**: nginx-multisite defines a custom 'lineinfile' resource - needs migration to ansible.builtin.lineinfile module
- **Git Repository Cloning**: fastapi-tutorial clones from GitHub - migrate to ansible.builtin.git module
- **Systemd Service Management**: Custom systemd service file creation and management - migrate to ansible.builtin.systemd and ansible.builtin.template modules
- **PostgreSQL Database Setup**: Database and user creation with SQL commands - migrate to community.postgresql.* modules

### Migration Order

1. **cache** (Priority 1: Low complexity, standalone service, clear dependency mapping)
2. **fastapi-tutorial** (Priority 2: Moderate complexity, database integration, systemd service management)
3. **nginx-multisite** (Priority 3: High complexity, multiple sites, SSL management, security hardening, custom resources)

### Assumptions

- The target environment will have internet access for package installation and Git repository cloning
- PostgreSQL will be installed on the same host as the FastAPI application (not using external database server)
- Self-signed certificates are acceptable for the target environment (not using Let's Encrypt or CA-signed certificates)
- The Fedora 42 development environment will be replaced with a RHEL 9 based system for production
- UFW firewall is the preferred firewall solution (not iptables or firewalld)
- The current hardcoded credentials are acceptable for development but will need proper secret management in production
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and the 'main' branch is stable
- The custom Redis configuration fixes in the cache cookbook are still necessary and not resolved in newer Redis versions
- The nginx sites will continue to use the same domain names (test.cluster.local, ci.cluster.local, status.cluster.local)
- The document root paths and directory structure will remain the same in the migrated environment
- Memcached and Redis will continue to run on the same host as nginx (not using external caching servers)
- The systemd service approach for FastAPI is preferred over other process management solutions
- The current Chef cookbook file structure (templates, files, attributes) can be directly mapped to Ansible role structure (templates, files, defaults)