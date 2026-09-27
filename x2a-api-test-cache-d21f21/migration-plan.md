# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external cookbook dependencies, and migrating security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers, with moderate complexity due to SSL certificate management, database setup, and security hardening requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory setup, configuration file patching via ruby_block, memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration - contains node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file - defines cookbook paths and cache settings
- `Vagrantfile`: Development environment provisioning - likely contains VM configuration for testing
- `vagrant-provision.sh`: Shell provisioning script - may contain additional setup commands for Vagrant

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules for memcached installation and management
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, ansible.builtin.template for redis.conf, and ansible.builtin.service modules

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - migrate to ansible.builtin.openssl_* modules or community.crypto collection
- **SSH Hardening**: Root login disabled and password authentication disabled via sed commands - migrate to ansible.builtin.lineinfile module
- **Firewall Configuration**: UFW rules managed via execute resources - migrate to community.general.ufw module
- **Fail2ban Configuration**: Template-based jail configuration - migrate to ansible.builtin.template module
- **Credential Types per Module**:
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded), application environment variables
  - nginx-multisite: SSL certificate generation (self-signed), no external credentials

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex regex-based configuration file manipulation - will need to be replaced with ansible.builtin.lineinfile or ansible.builtin.replace modules with multiple tasks
- **Dynamic Site Generation**: The nginx-multisite cookbook dynamically creates sites based on node attributes - will require Ansible loops and conditional logic
- **Service Dependencies**: PostgreSQL must be running before database user creation - requires proper task ordering and handlers in Ansible
- **File Permissions**: Complex SSL certificate permissions (ssl-cert group) - ensure proper ansible.builtin.file module usage with group management

### Migration Order

1. **cache** (low risk, high value) - Straightforward package installation with configuration templates, minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database setup, requires careful handling of Python virtual environments and systemd services
3. **nginx-multisite** (high complexity, dependencies) - Complex multi-site configuration with SSL, security hardening, and firewall rules - depends on understanding of all site requirements

### Assumptions

- The target environment will have internet access for package installation and git repository cloning
- SSL certificates are intended to be self-signed for development/testing environments (production may require different certificate management)
- The PostgreSQL and Redis services are intended to run on the same hosts as the applications (no external database servers)
- The UFW firewall configuration assumes standard HTTP/HTTPS ports and SSH access requirements
- The fail2ban configuration uses default jail settings with template customization
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible during migration
- The nginx sites configuration in solo.json represents the complete set of required virtual hosts
- The security hardening settings (SSH configuration, sysctl parameters) are appropriate for the target environment
- The Chef cookbook versions specified in Berksfile represent stable, compatible versions that can be replicated with equivalent Ansible modules