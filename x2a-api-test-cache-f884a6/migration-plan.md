# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and preserving security configurations. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, custom lineinfile resource

- **cache**:
    - Description: Caching layer configuration with memcached and Redis services, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service setup, Redis with password authentication (redis_secure_password_123), custom Redis configuration cleanup via ruby_block, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef node configuration with site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443)
- `vagrant-provision.sh`: Automated Chef installation and Berkshelf dependency resolution script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations). Default to Red Hat Enterprise Linux 9 for Ansible migration.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or local development environment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Currently commented out, replace with community.crypto.openssl_* modules for certificate generation

### Security Considerations
- **Hardcoded credentials**: Redis password "redis_secure_password_123" in cache cookbook requires vault management
- **PostgreSQL credentials**: FastAPI database password "fastapi_password" needs secure storage
- **SSL certificate management**: Self-signed certificates for development, production certificates need proper management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve in Ansible
- **Firewall configuration**: UFW rules for SSH (22), HTTP (80), HTTPS (443) - migrate to ansible.posix.firewalld or community.general.ufw
- **Fail2ban configuration**: Intrusion prevention rules need migration to Ansible templates
- **Sysctl security tuning**: Kernel parameter hardening via /etc/sysctl.d/99-security.conf

### Technical Challenges
- **Custom Ruby resource**: The lineinfile.rb custom resource needs replacement with ansible.builtin.lineinfile module
- **Ruby block hacks**: Redis configuration cleanup in cache cookbook uses Ruby code that needs conversion to Ansible tasks
- **Template migration**: 5 ERB templates in nginx-multisite need conversion to Jinja2 format
- **Service dependencies**: PostgreSQL must be running before FastAPI application starts - use Ansible handlers and dependencies
- **Git repository cloning**: FastAPI tutorial clones from GitHub, ensure Ansible has git module access
- **Virtual environment management**: Python venv creation and pip installation needs careful ordering in Ansible

### Migration Order
1. **cache cookbook** (low risk, minimal dependencies) - Start with memcached and Redis services
2. **fastapi-tutorial cookbook** (moderate complexity) - PostgreSQL and Python application setup
3. **nginx-multisite cookbook** (high complexity, security dependencies) - Complex templates, security hardening, SSL management

### Assumptions
- The target environment will have internet access for package installation and git repository cloning
- PostgreSQL service will be available on the target system or installed as part of the migration
- SSL certificates in production will be provided externally or generated via Let's Encrypt (not self-signed)
- The Vagrant development environment setup will be replaced with Ansible testing via molecule or similar
- External cookbook dependencies (nginx, memcached, redisio) functionality will be replicated using native Ansible modules
- The current Fedora 42 Vagrant box choice suggests comfort with RPM-based systems, but cookbook metadata indicates Ubuntu/CentOS support
- Network configuration (192.168.121.10 private network) may need adjustment for target environment
- The /chef-repo path structure will be replaced with standard Ansible directory layout (/etc/ansible or project-specific structure)
- Berkshelf dependency resolution will be replaced with Ansible Galaxy or direct role inclusion
- Chef Solo's local execution model will transition to Ansible's SSH-based or local execution model