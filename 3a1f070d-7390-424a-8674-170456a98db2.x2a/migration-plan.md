# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI tutorial application with PostgreSQL backend. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external cookbook dependencies, and preserving security configurations including fail2ban, UFW firewall, and SSH hardening.

**Migration Complexity**: Medium (3 cookbooks, external dependencies, security configurations)
**Estimated Timeline**: 2-3 weeks for complete migration and testing
**Target Environment**: Fedora 42 (based on Vagrantfile), adaptable to RHEL/CentOS family

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with Memcached and Redis authentication, including custom Redis configuration fixes and log directory management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication (redis_secure_password_123), custom config file manipulation, log directory creation, service enablement

- **fastapi-tutorial**:
    - Description: FastAPI tutorial application deployment with PostgreSQL database, Python virtual environment, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python venv creation, PostgreSQL database/user creation, systemd service configuration, environment file management

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate generation, fail2ban integration, UFW firewall, SSH hardening, custom lineinfile resource

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef node attributes defining site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443)
- `vagrant-provision.sh`: Automated Chef installation and cookbook dependency resolution using Berkshelf

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: libvirt/KVM (configured in Vagrantfile with 2GB RAM, 2 CPUs)
- **Cloud Platform**: Not specified (local development environment)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **berkshelf**: Replace with ansible-galaxy for role dependency management
- **chef-solo**: Replace with ansible-playbook execution

### Security Considerations

- **Hardcoded Credentials**: Redis password 'redis_secure_password_123' in cache cookbook - migrate to Ansible Vault
- **PostgreSQL Credentials**: Database password 'fastapi_password' in fastapi-tutorial cookbook - migrate to Ansible Vault  
- **SSL Certificate Management**: Self-signed certificate generation for 3 domains (test.cluster.local, ci.cluster.local, status.cluster.local) - consider Let's Encrypt integration
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve in Ansible
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to ansible.posix.ufw module
- **Fail2ban Integration**: Jail configuration for nginx protection - migrate to community.general.fail2ban module
- **Vault/secrets management**: 
  - **cache module**: 1 Redis password credential detected
  - **fastapi-tutorial module**: 1 PostgreSQL password credential detected
  - **nginx-multisite module**: SSL certificate paths and self-signed cert generation (3 certificates)

### Technical Challenges

- **Custom Redis Configuration Manipulation**: The cache cookbook uses Ruby blocks to modify Redis config files by removing specific lines - requires Ansible lineinfile module with regex patterns
- **Complex Template Variables**: nginx-multisite uses nested site configurations with SSL settings - requires careful Jinja2 template conversion
- **Custom Resource Migration**: The lineinfile.rb custom resource needs conversion to ansible.builtin.lineinfile module
- **Berkshelf Dependency Resolution**: External cookbook dependencies need mapping to Ansible Galaxy roles or custom implementations
- **Service Orchestration**: Chef's notifies/subscribes pattern for service reloads needs conversion to Ansible handlers
- **File Synchronization**: Vagrant rsync folder sync needs adaptation for Ansible deployment methods

### Migration Order

1. **nginx-multisite** (foundational web server, moderate complexity, well-defined templates)
2. **cache** (moderate complexity, custom Redis configuration challenges)
3. **fastapi-tutorial** (highest complexity, database setup, application deployment, systemd service management)

### Assumptions

- Target systems will have Python 3 and pip available for FastAPI application deployment
- PostgreSQL service management patterns are consistent across target distributions
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt integration)
- The custom Redis configuration fixes in the cache cookbook are still necessary for the target Redis version
- UFW firewall is available and preferred over iptables on target systems
- Systemd is the service manager on target systems for FastAPI application service management
- The Vagrant development workflow will be replaced with direct Ansible playbook execution
- Git repository access for FastAPI tutorial cloning will be available from target systems
- The three-site configuration (test, ci, status subdomains) represents the complete scope of nginx virtual hosts
- Berkshelf vendor directory structure can be replaced with Ansible Galaxy role installation
- Chef Solo's file cache directory (/var/chef-solo) functionality is not required in Ansible equivalent