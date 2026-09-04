# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and preserving security configurations. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **cache**:
    - Description: Caching services configuration with memcached and Redis authentication, including custom Redis configuration fixes and log directory management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis config cleanup via ruby_block, log directory creation

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban integration, UFW firewall configuration, SSH hardening, self-signed certificate generation, custom lineinfile resource

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef node attributes defining site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, port forwarding, and rsync syncing
- `vagrant-provision.sh`: Automated Chef installation and cookbook dependency resolution using Berkshelf

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations)
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified (local development environment focused)

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Currently commented out, replace with community.crypto.openssl_* modules for certificate generation

### Security Considerations
- **Hardcoded credentials**: Redis password 'redis_secure_password_123' in cache cookbook requires Ansible Vault migration
- **PostgreSQL credentials**: Database password 'fastapi_password' in fastapi-tutorial cookbook needs vault protection
- **SSL certificate management**: Self-signed certificate generation for 3 domains (test.cluster.local, ci.cluster.local, status.cluster.local)
- **SSH hardening**: Root login disabled, password authentication disabled
- **Firewall configuration**: UFW rules for SSH (22), HTTP (80), HTTPS (443)
- **Fail2ban integration**: Jail configuration for nginx protection
- **Sysctl security settings**: Kernel parameter hardening via /etc/sysctl.d/99-security.conf
- **Vault/secrets management**: 
  - cache module: 1 Redis password credential
  - fastapi-tutorial module: 1 PostgreSQL password credential
  - nginx-multisite module: 3 SSL certificate/key pairs (self-signed)
  - Total: 5 credential items requiring Ansible Vault protection

### Technical Challenges
- **Custom Ruby resource**: nginx-multisite cookbook contains a custom 'lineinfile' resource that needs conversion to ansible.builtin.lineinfile module
- **Ruby block logic**: Cache cookbook uses ruby_block for Redis configuration cleanup - requires conversion to Ansible tasks with regex replacements
- **Git repository cloning**: FastAPI tutorial clones from GitHub - needs ansible.builtin.git module with proper error handling
- **Systemd service management**: Custom systemd service file creation and daemon-reload orchestration
- **Template conversion**: 5 ERB templates need conversion to Jinja2 (nginx.conf.erb, security.conf.erb, site.conf.erb, fail2ban.jail.local.erb, sysctl-security.conf.erb)
- **File resource management**: Static HTML files for each site need proper Ansible file module handling
- **Berkshelf dependency resolution**: External cookbook dependencies need manual conversion to equivalent Ansible collections

### Migration Order
1. **cache** (low risk, standalone caching services)
2. **nginx-multisite** (moderate complexity, security configurations and templates)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions
- Target systems will have Python 3 available for Ansible execution
- PostgreSQL installation and configuration will be handled by separate database role or existing infrastructure
- SSL certificates in production will be replaced with proper CA-signed certificates (current implementation uses self-signed)
- Berkshelf vendor directory (/chef-repo/cookbooks-*/cookbooks) suggests external cookbook integration that may require additional Ansible collection dependencies
- Vagrant development environment will be replaced with Ansible-based local testing (molecule or vagrant with ansible provisioner)
- Chef license acceptance (CHEF_LICENSE=accept-silent) indicates enterprise Chef usage that won't be needed in Ansible migration
- Network configuration (192.168.121.10 private network) and port forwarding (8080->80, 8443->443) will be maintained in new development environment
- File permissions and ownership patterns (www-data user/group, ssl-cert group) assume Debian/Ubuntu target systems
- The commented-out ssl_certificate cookbook dependency suggests future certificate management requirements not currently implemented