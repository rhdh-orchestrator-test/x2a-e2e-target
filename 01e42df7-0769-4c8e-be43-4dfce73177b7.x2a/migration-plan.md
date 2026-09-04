# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure setup for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible playbooks/roles, managing external dependencies, and addressing security configurations including SSL certificates and firewall rules. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **cache**:
    - Description: Caching services configuration with memcached and Redis authentication, includes Redis configuration fixes and log directory management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration cleanup, log directory creation

- **fastapi-tutorial**:
    - Description: FastAPI application deployment with PostgreSQL database, Python virtual environment, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python venv setup, PostgreSQL database and user creation, systemd service configuration, environment file with database credentials

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate generation, fail2ban integration, UFW firewall, SSH hardening, custom lineinfile resource

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef node attributes defining site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging
- `Vagrantfile`: Development environment using Fedora 42 with libvirt provider, port forwarding for HTTP/HTTPS
- `vagrant-provision.sh`: Automated Chef installation and Berkshelf dependency management script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations), with Fedora 42 used in development environment
- **Virtual Machine Technology**: libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or local development setup

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Commented out in Berksfile, replace with community.crypto.openssl_* modules for self-signed certificates

### Security Considerations
- **SSL Certificate Management**: Self-signed certificates generated for each site (test.cluster.local, ci.cluster.local, status.cluster.local) - migrate to community.crypto.openssl_certificate and community.crypto.openssl_privatekey modules
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.lineinfile module
- **Fail2ban Integration**: Custom jail configuration - migrate to community.general.ini_file module
- **Vault/secrets management**: For each module, credential patterns detected:
  - **cache**: 1 hardcoded Redis password (redis_secure_password_123) in recipe
  - **fastapi-tutorial**: 2 hardcoded passwords (PostgreSQL user: fastapi_password, database credentials in .env file)
  - **nginx-multisite**: SSL certificate generation with hardcoded subject information
  - **Total**: 3 modules with 4 credential instances requiring Ansible Vault migration

### Technical Challenges
- **Custom Ruby Resource**: nginx-multisite cookbook contains a custom lineinfile resource that needs conversion to ansible.builtin.lineinfile module
- **Redis Configuration Hack**: cache cookbook includes Ruby block for manual Redis config file manipulation - needs proper Ansible template approach
- **Complex Site Configuration**: Dynamic site generation based on node attributes requires Ansible loops and template variables
- **Berkshelf Dependency Resolution**: External cookbook dependencies need manual conversion to equivalent Ansible modules
- **Chef Solo to Ansible Conversion**: Node attributes and run_list concepts need mapping to Ansible inventory and playbook structure

### Migration Order
1. **cache** (low risk, straightforward service configuration)
2. **fastapi-tutorial** (moderate complexity, database setup and application deployment)
3. **nginx-multisite** (high complexity, custom resources, multiple integrations, security configurations)

### Assumptions
- Target systems will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require proper CA-signed certificates)
- The custom lineinfile resource functionality can be replaced with standard Ansible lineinfile module
- Redis configuration "hack" indicates potential issues with the redisio cookbook that may not exist with direct Ansible Redis configuration
- Vagrant development environment will be replaced with equivalent Ansible testing setup
- Network configuration (192.168.121.10, port forwarding) represents development setup and may differ in production
- PostgreSQL and Redis services will be managed directly by Ansible rather than through external roles
- The three-site configuration (test, ci, status subdomains) represents the complete scope of required sites
- Chef license acceptance requirement will not apply to Ansible migration
- Berkshelf vendor directory approach suggests cookbook dependencies are bundled, requiring individual module conversion rather than role dependencies