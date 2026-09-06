# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI application with PostgreSQL backend. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates, database credentials, and system hardening.

**Migration Complexity**: Medium-High (3-4 weeks)
**Timeline Estimate**: 3-4 weeks for complete migration including testing
**Team Coordination**: Requires coordination between web infrastructure, database, and security teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL termination for multiple subdomains (test.cluster.local, ci.cluster.local, status.cluster.local), security hardening with fail2ban and UFW firewall, self-signed certificate generation, and custom site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning, custom lineinfile resource

- **cache**:
    - Description: Caching layer configuration with Memcached and Redis services, Redis authentication setup, custom log directory management, and configuration file patching for Redis compatibility
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, memcached service, custom Redis config manipulation, log directory setup

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database backend, Python virtual environment setup, Git repository cloning, systemd service management, and database user provisioning
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python venv management, PostgreSQL database creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef node configuration with nginx site definitions, SSL paths, and security settings for fail2ban, UFW, and SSH hardening
- `solo.rb`: Chef Solo configuration specifying cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, network configuration for testing, and Chef provisioning
- `vagrant-provision.sh`: Automated Chef installation and cookbook dependency resolution using Berkshelf

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata.rb support declarations). Default to Red Hat Enterprise Linux 9 for production deployment.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or private cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules for site configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Berkshelf**: Replace with Ansible Galaxy for role dependency management
- **Chef Solo**: Replace with ansible-playbook execution

### Security Considerations

- **SSL Certificate Management**: Migration approach for self-signed certificate generation using openssl commands in Ansible tasks
- **Database Credentials**: For fastapi-tutorial module, identify credential patterns:
  - PostgreSQL password: 'fastapi_password' hardcoded in recipe (1 credential detected)
  - Redis authentication: 'redis_secure_password_123' hardcoded in cache recipe (1 credential detected)
  - Total: 2 hardcoded credentials requiring Ansible Vault migration
- **SSH Hardening**: Convert Chef execute resources for SSH configuration to ansible.posix.lineinfile tasks
- **Firewall Rules**: Convert UFW commands to community.general.ufw module tasks
- **Fail2ban Configuration**: Convert template-based fail2ban configuration to Ansible template tasks

### Technical Challenges

- **Custom Chef Resource Migration**: The nginx-multisite cookbook contains a custom 'lineinfile' resource that needs conversion to ansible.builtin.lineinfile module with equivalent functionality
- **Redis Configuration Patching**: The cache cookbook uses Ruby block manipulation of Redis config files - requires conversion to Ansible template or lineinfile tasks for configuration management
- **Multi-site SSL Certificate Generation**: Complex SSL certificate generation loop for multiple sites needs conversion to Ansible with_items or loop constructs
- **Chef Template Variables**: ERB templates need conversion to Jinja2 templates with variable mapping from Chef node attributes to Ansible variables
- **Service Dependency Management**: Chef notifies/subscribes patterns need conversion to Ansible handlers and notify mechanisms

### Migration Order

1. **cache** (Priority 1 - low risk, foundational service)
   - Simple service installation and configuration
   - Limited external dependencies
   - Clear credential patterns for Vault migration

2. **fastapi-tutorial** (Priority 2 - moderate complexity)
   - Application deployment with database setup
   - Python environment management
   - Systemd service configuration

3. **nginx-multisite** (Priority 3 - high complexity, multiple dependencies)
   - Complex multi-site configuration
   - SSL certificate management
   - Security hardening integration
   - Custom resource conversion required

### Assumptions

- **Operating System Compatibility**: Assuming target systems will be RHEL 9 family, but cookbooks specify Ubuntu/CentOS support - may require package name and service management adjustments
- **SSL Certificate Strategy**: Current implementation uses self-signed certificates for development - production deployment may require Let's Encrypt or corporate CA integration
- **Database Persistence**: FastAPI application database data persistence strategy not specified - may require backup/restore procedures during migration
- **Network Configuration**: Vagrant configuration specifies private network 192.168.121.10 - production network configuration requirements unclear
- **Service User Management**: Chef recipes run services as root or default users - may need to implement dedicated service users for security best practices
- **External Cookbook Dependencies**: Assuming community Ansible collections (community.general, ansible.posix) will provide equivalent functionality to Chef Supermarket cookbooks
- **Configuration Management**: Chef node attributes and solo.json configuration patterns need mapping to Ansible group_vars/host_vars structure
- **Template Migration**: ERB template syntax and Chef helper methods need manual conversion to Jinja2 with potential logic adjustments
- **Testing Strategy**: Current Vagrant-based testing approach needs conversion to molecule or similar Ansible testing framework