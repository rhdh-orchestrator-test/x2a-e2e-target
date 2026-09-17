# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters, custom nginx configuration templates

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: SSL certificate paths are configured but certificate provisioning method is unclear - implement proper certificate management strategy
- **SSH Hardening**: Root login disable and password authentication disable configurations need careful migration to avoid lockout
- **Firewall Rules**: UFW configuration with specific port allowances (22, 80, 443) requires precise Ansible firewall module implementation
- **Fail2ban Configuration**: Custom jail.local template needs migration to Ansible template module
- **Sysctl Security Parameters**: Security-focused kernel parameter tuning requires ansible.posix.sysctl module

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - this will require custom Ansible tasks using lineinfile or replace modules
- **Git Repository Management**: FastAPI tutorial uses git resource for application deployment - migrate to ansible.builtin.git module with proper change detection
- **Service Dependencies**: PostgreSQL service must be running before database operations - implement proper task ordering and handlers
- **Template Variable Mapping**: Chef ERB templates need conversion to Jinja2 with attribute-to-variable mapping
- **Multi-site Configuration**: Dynamic site creation based on node attributes requires Ansible loops and conditional logic

### Migration Order

1. **cache** (moderate complexity, standalone dependencies)
2. **fastapi-tutorial** (moderate complexity, database dependencies)
3. **nginx-multisite** (high complexity, security configurations, multiple templates)

### Assumptions

- SSL certificates are manually managed or obtained through external processes (no automated certificate provisioning visible in the cookbooks)
- The target environment has internet access for package installation and git repository cloning
- PostgreSQL installation and initial configuration is handled by system packages rather than custom compilation
- The Redis configuration patching in the ruby_block is still necessary in the target environment
- UFW is the preferred firewall solution (rather than iptables or firewalld)
- The application runs as root user (as specified in the systemd service file)
- Static HTML files for the nginx sites are provided via cookbook files and don't require dynamic generation
- The fail2ban jail configuration is sufficient for the security requirements
- Chef Solo node attributes in solo.json represent the desired production configuration values