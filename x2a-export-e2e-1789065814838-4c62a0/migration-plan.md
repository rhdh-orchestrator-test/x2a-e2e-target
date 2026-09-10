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
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database/user provisioning, systemd service management, environment file configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening (fail2ban, UFW firewall), and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to ansible.posix.ufw module
- **Fail2ban Integration**: Jail configuration for nginx protection - migrate to community.general.fail2ban
- **Sysctl Security Tuning**: Kernel parameter hardening via templates - migrate to ansible.posix.sysctl

### Technical Challenges

- **Custom Redis Configuration Manipulation**: The cache cookbook uses Ruby blocks to modify Redis config files post-installation - requires custom Ansible tasks with lineinfile or template modules
- **Multi-site SSL Certificate Generation**: Dynamic certificate creation per site requires loop-based certificate generation in Ansible
- **Service Dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper service ordering with handlers
- **File Permissions and Ownership**: Complex SSL certificate permissions (ssl-cert group) need careful migration to Ansible file modules
- **Template Migration**: ERB templates need conversion to Jinja2 format for nginx.conf, security.conf, and fail2ban configurations

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security hardening, depends on SSL certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in Chef metadata
- Self-signed certificates are acceptable for development/internal use (production may require CA-signed certificates)
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without changing the actual credential values
- UFW firewall is the preferred firewall solution (vs. iptables or firewalld)
- Systemd is available on target systems for service management
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available during migration
- Current Chef Solo deployment model will be replaced with Ansible playbook execution
- Development environment provisioning via Vagrant is not required in the Ansible migration (focus on production deployment)