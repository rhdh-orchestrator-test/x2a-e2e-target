# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis authentication, including custom Redis configuration fixes and log directory management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached integration, Redis with authentication (password: redis_secure_password_123), custom config file manipulation, log directory creation

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening (fail2ban, UFW firewall), and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL password (fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate using ansible.posix.sysctl and lineinfile modules
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Integration**: Custom jail configuration - migrate using template module with Ansible templates
- **Database Credentials**: PostgreSQL user and database creation with embedded passwords - migrate to Ansible Vault with community.postgresql.* modules

### Technical Challenges

- **Custom Redis Configuration Manipulation**: The cache cookbook uses Ruby blocks to modify Redis config files post-installation - requires custom Ansible tasks with lineinfile or replace modules
- **Multi-site SSL Certificate Generation**: Dynamic certificate generation per site requires loop-based Ansible tasks with conditional certificate creation
- **Service Dependencies**: FastAPI service depends on PostgreSQL being ready - requires proper task ordering and service dependency management in Ansible
- **File Permissions and Ownership**: Complex SSL certificate permissions (ssl-cert group) need careful translation to Ansible file module parameters
- **Template Variable Mapping**: Chef ERB templates need conversion to Jinja2 with attribute mapping from Chef node attributes to Ansible variables

### Migration Order

1. **cache** (low risk, foundational service) - Redis and memcached are standalone services with minimal dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL infrastructure
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, requires nginx proxy configuration

### Assumptions

- Current Chef cookbooks are actively maintained and represent the desired end state
- SSL certificates are acceptable as self-signed for development/internal use (production may require CA-signed certificates)
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without service disruption
- Ubuntu/CentOS package names and service management are consistent with current Chef cookbook assumptions
- The three configured sites (test.cluster.local, ci.cluster.local, status.cluster.local) represent the complete site inventory
- Vagrant development environment workflow will be replaced with Ansible playbook execution
- No external Chef Server dependencies exist (cookbook uses Chef Solo)
- Current firewall rules (SSH, HTTP, HTTPS only) represent complete security requirements
- Python virtual environment approach is preferred over system-wide Python package installation