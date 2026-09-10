# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and SSH configuration management
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban jail configuration, UFW firewall rules, SSH hardening (root login disabled, password auth disabled), sysctl security parameters

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service setup, Redis with password authentication (requirepass), custom Redis configuration patching via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **PostgreSQL**: Replace with community.postgresql.* collection modules
- **Python/pip packages**: Replace with ansible.builtin.pip module

### Security Considerations

- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipe files - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths defined in attributes (/etc/ssl/certs, /etc/ssl/private) - implement proper certificate deployment with Ansible Vault for private keys
- **SSH hardening**: Root login disabled and password authentication disabled - preserve these security configurations in Ansible
- **Firewall rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS) - migrate to ansible.posix.ufw module
- **fail2ban configuration**: Custom jail.local template - migrate template to Ansible with ansible.builtin.template module
- **Database credentials**: PostgreSQL user and database creation with embedded passwords - migrate to Ansible Vault with community.postgresql modules

### Technical Challenges

- **Redis configuration patching**: The cache cookbook uses a ruby_block to manually edit Redis configuration files, removing specific directives - this will need custom Ansible tasks with ansible.builtin.lineinfile or ansible.builtin.replace modules
- **Git repository management**: FastAPI cookbook clones from GitHub with sync action - migrate to ansible.builtin.git module with proper version control
- **Systemd service creation**: Custom systemd service file creation for FastAPI application - migrate to ansible.builtin.systemd module with template deployment
- **Multi-site nginx configuration**: Template-driven virtual host creation for multiple SSL sites - migrate to ansible.builtin.template with loop constructs
- **Database initialization**: PostgreSQL database and user creation with embedded SQL commands - migrate to community.postgresql collection with proper idempotency

### Migration Order

1. **cache** (low risk, foundational service) - Redis and memcached setup with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL certificate management
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, Git integration, and systemd service management

### Assumptions

- SSL certificates are manually managed and placed in /etc/ssl/certs and /etc/ssl/private directories - certificate provisioning process not defined in Chef cookbooks
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) is accessible and contains a requirements.txt file for Python dependencies
- PostgreSQL service is expected to be running locally on the same host as the FastAPI application
- The target environment has internet access for package installation and Git repository cloning
- UFW firewall service is available on the target Ubuntu systems
- fail2ban service and configuration directories exist on target systems
- The nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) resolve to the target server or load balancer
- Static HTML files for each site are provided in the cookbook files directory and will need to be migrated as Ansible static files
- Redis configuration file location is standardized at /etc/redis/6379.conf across target environments
- Python 3 virtual environment creation is supported on target systems
- Systemd is the service manager on target systems for the FastAPI application service