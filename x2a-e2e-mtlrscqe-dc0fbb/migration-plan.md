# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef Solo configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 3-4 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and self-signed certificate generation for development
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, custom lineinfile resource

- **cache**:
    - Description: Caching layer with memcached and Redis services, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service, Redis 6379 with password authentication, custom Redis configuration cleanup via ruby_block, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application with PostgreSQL database, systemd service management, and virtual environment setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook references
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443), and rsync folder synchronization
- `vagrant-provision.sh`: Automated Chef installation and Berkshelf dependency resolution script

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for standardization.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises virtualization setup

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Solo runtime**: Replace with Ansible playbook execution via ansible-playbook command
- **Berkshelf dependency management**: Replace with ansible-galaxy for external role dependencies

### Security Considerations

- **Hardcoded credentials in cache cookbook**: Redis password 'redis_secure_password_123' needs migration to Ansible Vault
- **PostgreSQL credentials in fastapi-tutorial**: Database password 'fastapi_password' requires Vault encryption
- **SSL certificate management**: Self-signed certificate generation logic needs conversion to community.crypto.openssl_* modules
- **SSH hardening configurations**: Root login disable and password authentication disable need migration to ansible.posix.sysctl and lineinfile modules
- **Fail2ban and UFW configurations**: Security templates need conversion to Jinja2 format
- **Vault/secrets management**: 
  - **nginx-multisite**: 0 hardcoded credentials detected (uses self-signed certs)
  - **cache**: 1 Redis password in recipes/default.rb requiring Vault migration
  - **fastapi-tutorial**: 2 credentials (PostgreSQL user password, database connection string) requiring Vault encryption

### Technical Challenges

- **Custom lineinfile resource**: The nginx-multisite cookbook includes a custom Chef resource (resources/lineinfile.rb) that needs conversion to ansible.builtin.lineinfile module with equivalent functionality
- **Ruby block configuration fixes**: The cache cookbook uses ruby_block to manipulate Redis configuration files, requiring conversion to ansible.builtin.replace or ansible.builtin.lineinfile tasks
- **Template variable mapping**: Chef ERB templates need conversion to Jinja2 with node attribute references changed to Ansible variable syntax
- **Service notification patterns**: Chef's notifies/subscribes patterns need conversion to Ansible handlers and notify mechanisms
- **Git repository cloning**: FastAPI tutorial uses Chef git resource requiring conversion to ansible.builtin.git module
- **Systemd service management**: Custom systemd unit file creation needs migration to ansible.builtin.systemd module

### Migration Order

1. **cache cookbook** (low risk, foundational service)
   - Simple service installation and configuration
   - Limited external dependencies
   - Clear Redis/memcached service patterns

2. **fastapi-tutorial cookbook** (moderate complexity)
   - Python application deployment patterns
   - Database integration requirements
   - Systemd service management

3. **nginx-multisite cookbook** (high complexity, multiple dependencies)
   - Complex multi-site configuration
   - SSL certificate management
   - Security hardening integration
   - Custom resource conversion requirements

### Assumptions

- **Operating System Standardization**: Assuming migration to RHEL 9 family despite cookbook support for both Ubuntu and CentOS, requiring package name adjustments (apt vs yum/dnf)
- **External Cookbook Availability**: Assuming equivalent Ansible Galaxy roles exist for nginx, memcached, and Redis functionality, or custom role development will be required
- **Development Environment**: Vagrant/libvirt setup suggests on-premises development environment, but production target environment is unspecified
- **SSL Certificate Strategy**: Self-signed certificates are used for development - production migration may require Let's Encrypt or corporate CA integration
- **Database Migration**: PostgreSQL setup assumes local installation, but production may require external database connectivity
- **Network Configuration**: Hardcoded IP addresses (192.168.121.10) and domain names (*.cluster.local) suggest internal/development environment - production networking requirements unclear
- **Service Discovery**: No service discovery mechanism present, assuming static configuration approach will continue
- **Monitoring Integration**: No monitoring or logging aggregation present in current setup, may need addition during migration
- **Backup Strategy**: No backup procedures defined for PostgreSQL or Redis data, requiring addition in Ansible implementation
- **High Availability**: Single-node deployment pattern suggests no HA requirements, but production may need clustering considerations