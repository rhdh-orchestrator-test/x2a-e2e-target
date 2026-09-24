# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW firewall, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services configuration with Redis authentication and Memcached, including custom Redis configuration fixes and log directory management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, Memcached service, custom Redis configuration patching via ruby_block, log directory creation with proper ownership

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file generation

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run configuration with run_list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning configuration for local testing
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence for development)
- **Cloud Platform**: Not specified (appears to be designed for on-premises or generic cloud deployment)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Solo execution model**: Replace with Ansible playbook execution targeting specific host groups

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH security configuration**: Root login disabled and password authentication disabled via direct file editing - use ansible.posix.sshd_config module
- **Firewall rules**: UFW commands executed directly - replace with community.general.ufw module
- **Fail2ban configuration**: Template-based jail.local configuration - use community.general.fail2ban module
- **Database credentials**: PostgreSQL user creation with embedded passwords - migrate to Ansible Vault and postgresql_* modules

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses a ruby_block to manually edit Redis configuration files - requires conversion to Ansible lineinfile or template modules with proper configuration management
- **Complex nginx site management**: Dynamic site creation with SSL certificate generation and symlink management - requires careful conversion to ansible.builtin.template and ansible.builtin.file modules
- **Git repository cloning with dependency installation**: FastAPI cookbook clones repository and installs Python dependencies - needs conversion to ansible.builtin.git and ansible.builtin.pip modules
- **Service dependency management**: PostgreSQL must be running before database operations - requires proper task ordering and handlers in Ansible
- **File ownership and permissions**: Multiple cookbooks manage file ownership (www-data, redis, ssl-cert groups) - ensure proper user/group management in target environment

### Migration Order

1. **cache** (low risk, foundational service): Migrate Redis and Memcached services first as they have minimal external dependencies and are used by other services
2. **fastapi-tutorial** (moderate complexity): Migrate the Python application and PostgreSQL database setup, depends on cache services
3. **nginx-multisite** (high complexity): Migrate last due to SSL certificate dependencies, security configurations, and integration with other services

### Assumptions

- Target environment will have similar user accounts (www-data, redis) or these will need to be created during migration
- Self-signed certificates are acceptable for development; production deployment may require different certificate management strategy
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without changing the actual credential values
- UFW firewall is acceptable for the target environment (may need iptables alternative for some distributions)
- Python 3 virtual environment approach is still preferred over system packages or containers
- Systemd is available on target systems for service management
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available during and after migration
- Current Chef Solo execution model can be replaced with standard Ansible playbook execution without significant workflow changes