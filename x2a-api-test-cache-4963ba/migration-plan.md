# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef Solo configuration that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL termination, multi-site configuration, security hardening (fail2ban, UFW firewall), and self-signed certificate generation for development environments
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: SSL-enabled virtual hosts for test.cluster.local, ci.cluster.local, and status.cluster.local; fail2ban intrusion prevention; UFW firewall configuration; SSH hardening; sysctl security tuning; custom lineinfile resource

- **cache**:
    - Description: Caching services configuration with Memcached and Redis, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service setup; Redis 6379 with password authentication (redis_secure_password_123); custom Redis configuration cleanup via ruby_block; log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 virtual environment; Git repository cloning from https://github.com/dibanez/fastapi_tutorial.git; PostgreSQL database and user creation; systemd service management; environment configuration file

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook references
- `solo.json`: Chef Solo run list configuration and node attributes including nginx site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443), and rsync folder synchronization
- `vagrant-provision.sh`: Automated provisioning script that installs Chef, Berkshelf, downloads dependencies, and executes Chef Solo

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for production deployment.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or private cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **External Git Repository**: https://github.com/dibanez/fastapi_tutorial.git - verify repository availability and access requirements

### Security Considerations

- **Hardcoded Credentials**: Redis password 'redis_secure_password_123' in cache/recipes/default.rb - migrate to Ansible Vault
- **PostgreSQL Credentials**: Database password 'fastapi_password' in fastapi-tutorial/recipes/default.rb - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Security Configuration**: Root login disabled, password authentication disabled - maintain these security settings in Ansible
- **Firewall Rules**: UFW configuration for HTTP/HTTPS/SSH - replicate with ansible.posix.firewalld or community.general.ufw modules
- **Fail2ban Configuration**: Intrusion prevention system - migrate jail.local template to Ansible template
- **Sysctl Security Tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module

**Vault/secrets management**: 
- cache module: 1 Redis password credential detected
- fastapi-tutorial module: 2 credentials detected (PostgreSQL user password, database connection string)
- nginx-multisite module: SSL certificate paths and self-signed certificate generation (3 certificate/key pairs for test, ci, status subdomains)

### Technical Challenges

- **Custom Ruby Block Logic**: cache cookbook contains Ruby code for Redis configuration cleanup - requires translation to Ansible lineinfile or replace modules
- **Custom Chef Resource**: nginx-multisite cookbook includes custom 'lineinfile' resource - replace with ansible.builtin.lineinfile module
- **Template Migration**: 5 ERB templates need conversion to Jinja2 format (nginx.conf.erb, site.conf.erb, security.conf.erb, fail2ban.jail.local.erb, sysctl-security.conf.erb)
- **Service Dependencies**: PostgreSQL must be running before FastAPI application starts - implement proper task ordering and handlers
- **Git Repository Access**: Ensure network access to GitHub repository during deployment
- **Package Manager Differences**: Chef recipes assume apt package manager (Ubuntu/Debian) - adapt for target RHEL 9 with dnf/yum

### Migration Order

1. **cache** (low risk, foundational service)
   - Simple service installation and configuration
   - No complex dependencies
   - Required by other applications

2. **nginx-multisite** (moderate complexity, security-critical)
   - Core web server functionality
   - Security hardening components
   - SSL certificate management
   - Template conversions required

3. **fastapi-tutorial** (high complexity, application-specific)
   - Database dependencies
   - Application deployment logic
   - Service management
   - Git repository integration

### Assumptions

- Target environment has internet access for package installation and Git repository cloning
- PostgreSQL service will be managed by the same Ansible playbook or is available as a managed service
- Self-signed certificates are acceptable for development/testing environments
- The FastAPI tutorial application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- UFW firewall is preferred over firewalld for the target environment
- The target RHEL 9 environment can accommodate the Ubuntu/Debian-focused cookbook logic with appropriate package name translations
- Vagrant development environment will be replaced with Ansible testing framework or molecule
- Chef Berkshelf dependency management will be replaced with Ansible Galaxy or direct module usage
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the actual production requirements
- SSL certificate paths (/etc/ssl/certs, /etc/ssl/private) are standard and acceptable for the target environment
- Redis authentication is required in the production environment
- Fail2ban and SSH hardening configurations represent actual security requirements, not just examples