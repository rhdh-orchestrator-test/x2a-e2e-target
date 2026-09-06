# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI tutorial application with PostgreSQL backend. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates, firewall rules, and SSH hardening.

**Migration Complexity**: Medium-High (3 cookbooks, external dependencies, security configurations, SSL management)
**Estimated Timeline**: 3-4 weeks (1 week per cookbook + integration testing)
**Target Environment**: Fedora 42 (based on Vagrantfile), KVM/libvirt virtualization

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL termination for multiple subdomains (test.cluster.local, ci.cluster.local, status.cluster.local), security hardening with fail2ban and UFW firewall, SSH configuration hardening, and self-signed SSL certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site virtual host configuration, self-signed SSL certificates, fail2ban intrusion prevention, UFW firewall with HTTP/HTTPS/SSH rules, SSH root login disable, password authentication disable, sysctl security tuning, custom lineinfile resource

- **cache**:
    - Description: Caching services configuration with Memcached and Redis, including Redis authentication, custom log directory setup, and configuration file manipulation to remove deprecated Redis directives
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration cleanup via ruby_block, Redis log directory creation with proper ownership

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database backend, including Git repository cloning, Python virtual environment setup, database user provisioning, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 virtual environment, Git repository cloning from GitHub, PostgreSQL database and user creation, systemd service management, environment configuration file (.env), uvicorn ASGI server

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook references
- `solo.json`: Chef Solo run list configuration and node attributes including nginx site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup for Fedora 42 with libvirt provider, network configuration (192.168.121.10), and port forwarding (80→8080, 443→8443)
- `vagrant-provision.sh`: Automated Chef installation and provisioning script with Berkshelf dependency management

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration, though cookbooks support Ubuntu ≥18.04 and CentOS ≥7.0)
- **Virtual Machine Technology**: KVM/libvirt (configured in Vagrantfile with 2GB RAM, 2 CPUs)
- **Cloud Platform**: Not specified (local development environment)

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or manual configuration with ansible.builtin.template
- **ssl_certificate (~> 2.1)**: Currently commented out, replace with community.crypto.openssl_* modules for SSL certificate generation

### Security Considerations
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands need migration to community.crypto.openssl_certificate and community.crypto.openssl_privatekey modules
- **Firewall Configuration**: UFW rules (SSH, HTTP, HTTPS) need migration to community.general.ufw module
- **SSH Hardening**: Root login disable and password authentication disable need migration to ansible.posix.lineinfile module
- **Fail2ban Configuration**: Template-based jail.local configuration needs migration to ansible.builtin.template module
- **Sysctl Security Tuning**: Security kernel parameters need migration to ansible.posix.sysctl module
- **Vault/secrets management**: 
  - **cache module**: 1 hardcoded Redis password ('redis_secure_password_123') in recipes/default.rb
  - **fastapi-tutorial module**: 1 hardcoded PostgreSQL password ('fastapi_password') in recipes/default.rb
  - **nginx-multisite module**: No hardcoded credentials detected, uses self-signed certificates
  - **Total credentials detected**: 2 passwords requiring Ansible Vault migration

### Technical Challenges
- **Custom Chef Resource Migration**: The lineinfile.rb custom resource in nginx-multisite needs replacement with ansible.builtin.lineinfile module
- **Ruby Block Logic**: Complex Ruby code in cache cookbook for Redis configuration cleanup needs conversion to Ansible tasks with ansible.builtin.replace or ansible.builtin.lineinfile
- **Template Variable Mapping**: ERB templates need conversion to Jinja2 with variable name adjustments
- **Service Dependencies**: PostgreSQL service dependency in fastapi-tutorial needs proper Ansible handler configuration
- **Git Repository Cloning**: Chef git resource needs migration to ansible.builtin.git module with proper authentication handling
- **Python Virtual Environment**: Chef execute resources for venv creation and pip installation need migration to ansible.builtin.pip module with virtualenv parameters
- **Systemd Service Management**: Template-based systemd service creation needs migration to ansible.builtin.template with proper handler notifications

### Migration Order
1. **cache** (Priority 1: Low complexity, standalone service, good starting point)
2. **nginx-multisite** (Priority 2: Medium complexity, security configurations, custom resource migration)
3. **fastapi-tutorial** (Priority 3: High complexity, multiple dependencies, database integration, systemd service management)

### Assumptions
- **Operating System Compatibility**: Cookbooks support multiple OS families (Ubuntu, CentOS) but Vagrantfile specifies Fedora 42 - need clarification on target OS for package manager selection
- **External Cookbook Versions**: Berksfile specifies version constraints for external cookbooks that may not directly map to Ansible module versions
- **SSL Certificate Requirements**: Currently using self-signed certificates for development - production deployment may require different certificate management strategy
- **Database Persistence**: PostgreSQL data persistence and backup strategies not defined in current Chef configuration
- **Network Configuration**: Vagrant-specific network settings (192.168.121.10) may not apply to production environment
- **Service User Management**: Some services run as root (FastAPI) which may need security review for production deployment
- **Git Repository Access**: FastAPI tutorial clones from public GitHub repository - private repositories would require authentication configuration
- **Python Dependencies**: requirements.txt file content not visible in current repository - may contain additional system dependencies
- **Redis Configuration Cleanup**: Ruby block hack for Redis config suggests compatibility issues that need investigation in Ansible implementation
- **Template File Content**: ERB template files not examined - may contain complex logic requiring careful Jinja2 conversion
- **File Permissions**: Some Chef resources use specific ownership (www-data, redis, ssl-cert group) that need verification on target OS
- **Berkshelf Vendor Process**: Current workflow uses 'berks vendor' to download dependencies - Ansible equivalent using ansible-galaxy needs configuration