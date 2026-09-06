# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and preserving security configurations. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

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
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service management, environment configuration

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL/TLS with self-signed certificates, fail2ban integration, UFW firewall, SSH hardening, custom lineinfile resource

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider and port forwarding
- `vagrant-provision.sh`: Automated Chef installation and cookbook dependency resolution script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified (local development environment focused)

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Replace with community.crypto.openssl_* modules for certificate generation

### Security Considerations
- **Hardcoded credentials**: Redis password "redis_secure_password_123" in cache cookbook requires vault management
- **PostgreSQL credentials**: Database password "fastapi_password" in fastapi-tutorial cookbook needs secure handling
- **SSL certificate management**: Self-signed certificate generation for 3 sites (test.cluster.local, ci.cluster.local, status.cluster.local)
- **SSH hardening**: Root login disabled, password authentication disabled
- **Firewall configuration**: UFW rules for SSH (22), HTTP (80), HTTPS (443)
- **Fail2ban integration**: Jail configuration for nginx protection
- **Sysctl security settings**: Kernel parameter hardening via /etc/sysctl.d/99-security.conf
- **Vault/secrets management**: 
  - **cache module**: 1 Redis password credential
  - **fastapi-tutorial module**: 1 PostgreSQL password credential
  - **nginx-multisite module**: 3 SSL certificate/key pairs for virtual hosts
  - Total: 5 credential items requiring Ansible Vault or external secret management

### Technical Challenges
- **Custom Chef resource migration**: The lineinfile.rb custom resource in nginx-multisite needs conversion to ansible.builtin.lineinfile module
- **Redis configuration cleanup**: Complex Ruby block for Redis config file manipulation requires equivalent Ansible tasks
- **Multi-site SSL certificate generation**: Coordinating certificate creation for 3 virtual hosts with proper file permissions
- **Service dependency management**: Ensuring PostgreSQL is ready before FastAPI application starts
- **Template variable mapping**: Converting ERB templates to Jinja2 with proper variable scoping
- **Berkshelf to Ansible Galaxy**: Migrating external cookbook dependencies to Ansible collections

### Migration Order
1. **cache cookbook** (low risk, standalone caching services)
2. **nginx-multisite cookbook** (moderate complexity, security configurations and SSL management)
3. **fastapi-tutorial cookbook** (high complexity, application deployment with database dependencies)

### Assumptions
- Target systems will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require CA-signed certificates)
- Redis password authentication is required and current password can be migrated to Ansible Vault
- PostgreSQL database will be managed locally on the same host as the FastAPI application
- Systemd is available on target systems for service management
- The FastAPI tutorial repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- UFW firewall is the preferred firewall solution (may need adaptation for RHEL-based systems using firewalld)
- Fail2ban configuration requirements remain consistent with current jail.local template
- The custom lineinfile resource functionality can be fully replaced with Ansible's built-in lineinfile module
- Development workflow using Vagrant can be replaced with molecule for Ansible role testing
- External cookbook dependencies (nginx, memcached, redisio) can be replaced with equivalent Ansible modules without functionality loss