# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW, and SSH access controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

**cache**:
- Description: Caching services configuration with memcached and Redis authentication, including custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis config file manipulation, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL password (fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificates referenced but not managed by cookbooks - implement certificate deployment strategy
- **SSH security configurations**: Root login disable and password authentication disable need careful migration to avoid lockout
- **Firewall rules**: UFW configuration requires proper sequencing to maintain connectivity during deployment
- **Fail2ban configuration**: Intrusion prevention rules need validation in Ansible equivalent

### Technical Challenges

- **Redis configuration manipulation**: The cache cookbook uses Ruby blocks to modify Redis config files post-installation - requires custom Ansible tasks with lineinfile or template modules
- **PostgreSQL database initialization**: Database and user creation commands use shell execution with conditional logic - migrate to postgresql_* modules with proper idempotency
- **Multi-site nginx configuration**: Template-driven virtual host generation needs conversion to Jinja2 templates with proper variable handling
- **Service dependency ordering**: Ensure PostgreSQL starts before FastAPI application, and nginx configuration is valid before service restart
- **File permissions and ownership**: Multiple file/directory operations with specific user/group assignments need careful mapping

### Migration Order

1. **cache** (low risk, standalone service)
   - Simple package installation and service management
   - Self-contained with minimal external dependencies
   
2. **nginx-multisite** (moderate complexity)
   - Security configurations require careful testing
   - Template migration and SSL certificate handling
   
3. **fastapi-tutorial** (high complexity, database dependencies)
   - Database initialization and application deployment
   - Service management and environment configuration
   - Depends on proper system setup from previous modules

### Assumptions

- SSL certificates are manually managed and placed in /etc/ssl/certs and /etc/ssl/private directories
- PostgreSQL service is available via system packages and does not require custom compilation
- The FastAPI tutorial repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Target systems have internet connectivity for package installation and Git repository cloning
- Current Chef Solo execution model will be replaced with Ansible playbook execution
- UFW firewall rules will not conflict with existing network security policies
- Redis and memcached services can use default system package versions rather than specific compiled versions
- The three virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) are intended for local development/testing rather than production DNS resolution
- System users (www-data, redis, postgres) exist or can be created by package installation
- The custom Redis configuration fixes in the cache cookbook are still necessary for the target Redis version