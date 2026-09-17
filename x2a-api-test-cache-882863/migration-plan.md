# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, including Git deployment and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening, and firewall configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes - contains site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: SSL certificates referenced in nginx configuration need secure deployment mechanism
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security settings
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - maintain equivalent iptables or firewalld rules
- **System Security**: fail2ban configuration and sysctl security tuning need preservation
- **Database Credentials**: PostgreSQL user creation with embedded passwords requires Ansible Vault integration

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this complex logic needs conversion to Ansible lineinfile or template tasks
- **Git Repository Deployment**: FastAPI cookbook clones from GitHub with specific revision handling - requires ansible.builtin.git module with proper change detection
- **Multi-site Nginx Configuration**: Dynamic site generation based on node attributes requires Jinja2 templating and loop constructs
- **Service Dependencies**: PostgreSQL must be running before FastAPI application starts - requires proper task ordering and handlers
- **File Permissions and Ownership**: Multiple cookbooks set specific user/group ownership (www-data, redis) - ensure target systems have these users

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security configurations, depends on SSL certificate deployment strategy
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- Target systems will have the same user accounts (www-data, redis) as assumed by the Chef cookbooks
- SSL certificates for the three domains (test.cluster.local, ci.cluster.local, status.cluster.local) will be provided through external certificate management
- PostgreSQL installation method (package vs. container) is not specified in the FastAPI cookbook
- The GitHub repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- Network connectivity requirements for external package repositories (supermarket.chef.io equivalents) are maintained
- The custom Redis configuration patching in the cache cookbook addresses specific version compatibility issues that may not apply to target Redis versions
- UFW firewall is acceptable on target systems, or equivalent firewalld rules can be substituted for RHEL-based systems
- The systemd service configuration for FastAPI is appropriate for the target environment