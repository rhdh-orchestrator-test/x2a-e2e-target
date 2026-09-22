# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached integration, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate management, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks
- **Chef Solo execution model**: Replace with Ansible playbook execution and inventory management

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL password (fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration with community.crypto collection
- **SSH hardening**: Root login disabled, password authentication disabled - maintain with ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban integration**: Jail configuration for nginx protection - use community.general.fail2ban module
- **Sysctl security tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module
- **SSL certificate permissions**: ssl-cert group management and proper file permissions (640 for private keys)

### Technical Challenges

- **Redis configuration patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or template modules
- **Multi-site nginx configuration**: Dynamic site generation based on node attributes requires Ansible loops and template generation
- **PostgreSQL database initialization**: Database and user creation commands need conversion to community.postgresql modules
- **Systemd service management**: Custom service file creation and daemon-reload handling requires ansible.builtin.systemd module
- **Git repository cloning with dependency installation**: FastAPI application deployment involves git clone followed by pip install in virtual environment - requires careful task ordering
- **Self-signed certificate generation**: OpenSSL certificate creation with proper file permissions and ownership needs community.crypto.x509_certificate module

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web server)
   - Establish base nginx configuration and SSL infrastructure
   - Implement security hardening (fail2ban, UFW, SSH)
   - Test multi-site virtual host configuration

2. **cache** (low-medium complexity, standalone services)
   - Migrate memcached installation and configuration
   - Implement Redis setup with authentication
   - Address custom configuration patching requirements

3. **fastapi-tutorial** (high complexity, application deployment)
   - Migrate PostgreSQL database setup
   - Implement Python application deployment pipeline
   - Configure systemd service management
   - Integrate with nginx reverse proxy configuration

### Assumptions

- The target environment will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+)
- Vagrant development environment will be replaced with molecule testing or similar Ansible testing framework
- External cookbook dependencies (nginx, memcached, redisio) functionality will be replicated using Ansible modules and community collections
- SSL certificates will initially remain self-signed but may be upgraded to Let's Encrypt in future iterations
- Database passwords and Redis authentication will be migrated to Ansible Vault for security
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the production site structure
- UFW firewall rules and fail2ban configuration represent production security requirements
- The FastAPI application's GitHub repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible during migration
- Chef Solo's node attribute system will be replaced with Ansible group_vars and host_vars structure
- The custom Redis configuration patching indicates specific Redis version compatibility requirements that must be maintained