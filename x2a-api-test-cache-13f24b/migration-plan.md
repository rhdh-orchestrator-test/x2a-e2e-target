# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI application with PostgreSQL backend. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including hardcoded credentials.

**Migration Complexity**: Medium-High (3 cookbooks, external dependencies, security hardening, SSL management)
**Estimated Timeline**: 3-4 weeks (1 week per cookbook + integration testing)
**Team Coordination**: Requires coordination between web infrastructure, security, and application teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL termination for multiple subdomains (test.cluster.local, ci.cluster.local, status.cluster.local), security hardening with fail2ban/UFW, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, security hardening (fail2ban, UFW, SSH hardening), custom lineinfile resource, ERB templates for nginx.conf and site configurations

- **cache**:
    - Description: Caching services configuration with Memcached and Redis authentication, includes Redis configuration workarounds and log directory management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with authentication (hardcoded password), Memcached service, Redis configuration file manipulation via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, systemd service management, and Git-based source deployment
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 virtual environment, PostgreSQL database and user creation, systemd service configuration, Git repository cloning, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes including site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443)
- `vagrant-provision.sh`: Automated Chef installation and Berkshelf dependency resolution script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for Ansible migration.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or private cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or manual configuration with ansible.builtin.template

### Security Considerations

- **Hardcoded Credentials**: 
  - Redis password: `redis_secure_password_123` in cache/recipes/default.rb
  - PostgreSQL password: `fastapi_password` in fastapi-tutorial/recipes/default.rb
  - Migration approach: Move to Ansible Vault encrypted variables
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands need conversion to ansible.builtin.openssl_* modules
- **SSH Security Hardening**: Root login disable and password authentication disable via sed commands need conversion to ansible.builtin.lineinfile
- **Firewall Configuration**: UFW commands need conversion to community.general.ufw module
- **Fail2ban Configuration**: Template-based configuration needs conversion to ansible.builtin.template with Jinja2

**Vault/secrets management**: 
- **cache module**: 1 Redis authentication password detected
- **fastapi-tutorial module**: 1 PostgreSQL user password detected
- **nginx-multisite module**: SSL certificate generation (no hardcoded secrets but certificate management required)

### Technical Challenges

- **Custom Chef Resource**: The `lineinfile.rb` custom resource in nginx-multisite needs conversion to ansible.builtin.lineinfile module
- **Ruby Block Workarounds**: Redis configuration manipulation via ruby_block in cache cookbook requires conversion to proper Ansible template management
- **Complex Template Variables**: ERB templates with Chef node attributes need conversion to Jinja2 templates with Ansible variables
- **Service Dependencies**: PostgreSQL service dependency for FastAPI application needs proper Ansible handler and dependency management
- **Git Repository Management**: FastAPI source code deployment via Git needs conversion to ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (Priority 1: Low complexity, standalone service, good starting point)
2. **fastapi-tutorial** (Priority 2: Medium complexity, database dependencies, application deployment patterns)
3. **nginx-multisite** (Priority 3: High complexity, custom resources, security hardening, SSL management, depends on application services)

### Assumptions

- Target environment will maintain Ubuntu/RHEL compatibility as specified in Chef cookbook metadata
- Self-signed certificates are acceptable for development/testing environments (production may require Let's Encrypt or CA-signed certificates)
- Current hardcoded passwords are development/testing credentials and will be replaced with proper secret management
- Libvirt/KVM virtualization platform will be maintained in target environment
- Network configuration (192.168.121.10, port forwarding) is specific to development environment and may need adjustment for production
- Chef Berkshelf dependency resolution process will be replaced with Ansible Galaxy or manual role management
- Current Chef Solo execution model will be replaced with Ansible playbook execution
- Ruby-based configuration manipulation (ruby_block resources) indicates potential configuration management gaps that need proper Ansible solutions
- The custom lineinfile resource suggests need for file manipulation that should be handled by standard Ansible modules
- Git-based application deployment pattern should be maintained but with proper Ansible change detection and rollback capabilities