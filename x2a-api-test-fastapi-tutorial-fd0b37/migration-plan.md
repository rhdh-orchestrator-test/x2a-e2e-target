# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching, and application deployment. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and system-level security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

**cache**:
- Description: Caching services configuration providing both memcached and Redis with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached service, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external supermarket dependencies
- `solo.json`: Chef Solo run list and node attributes configuration with site-specific overrides
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be generic Linux deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration templates
- **External Git Repository**: FastAPI tutorial from https://github.com/dibanez/fastapi_tutorial.git - use ansible.builtin.git module

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found requiring vault migration:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials
- **SSL Certificate Management**: SSL certificates referenced in nginx configuration need secure deployment strategy
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve in Ansible
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban Configuration**: Intrusion prevention with custom jail.local template
- **System Security**: Custom sysctl security parameters via template

### Technical Challenges

- **Redis Configuration Patching**: Complex ruby_block hack for Redis config file manipulation needs clean Ansible template solution
- **Multi-site Nginx Configuration**: Dynamic site generation from attributes requires Ansible loops and templates
- **PostgreSQL Database Initialization**: Database and user creation with proper idempotency
- **Systemd Service Management**: Custom service file creation and daemon-reload handling
- **File Permissions and Ownership**: Multiple www-data ownership requirements across different paths
- **Template Dependencies**: ERB templates need conversion to Jinja2 with different syntax

### Migration Order

1. **cache** (low risk, standalone service with clear dependencies)
2. **nginx-multisite** (moderate complexity, security configurations, multiple templates)
3. **fastapi-tutorial** (high complexity, database dependencies, application deployment)

### Assumptions

- SSL certificates are managed externally and will be available at specified paths (/etc/ssl/certs, /etc/ssl/private)
- PostgreSQL service installation and basic configuration is acceptable via package manager defaults
- The FastAPI tutorial Git repository will remain accessible and stable
- Current Chef Solo execution model can be replaced with Ansible playbook execution
- UFW and fail2ban packages are available in target distribution repositories
- Python 3 virtual environment approach is preferred over system-wide package installation
- Systemd is the target init system for service management
- The three subdomain sites (test, ci, status) will continue to use the same SSL certificate approach
- Database credentials can be migrated to Ansible Vault without application code changes
- Current file ownership patterns (www-data, root) are appropriate for the target environment