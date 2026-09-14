# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations including fail2ban, UFW firewall, and SSL certificate management.

**Estimated Timeline**: 4-6 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security hardening
**Team Coordination**: Requires coordination between web operations, application deployment, and security teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or direct package installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and ansible.builtin.template for configuration

### Security Considerations

- **SSH Hardening**: Migration of SSH configuration changes (disable root login, disable password authentication) to ansible.posix.sysctl and ansible.builtin.lineinfile modules
- **Firewall Management**: UFW firewall rules need conversion to community.general.ufw module
- **Fail2ban Configuration**: Template-based fail2ban jail configuration requires ansible.builtin.template module
- **SSL Certificate Management**: Self-signed certificate generation needs conversion to community.crypto.openssl_privatekey and community.crypto.x509_certificate modules
- **Vault/secrets management**: 
  - Hardcoded credentials identified in cache cookbook (Redis password: 'redis_secure_password_123')
  - PostgreSQL credentials in fastapi-tutorial cookbook (database password: 'fastapi_password')
  - SSL certificate generation uses hardcoded subject information
  - No encrypted data bags or Chef Vault usage detected

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - this will need to be converted to ansible.builtin.replace or ansible.builtin.lineinfile tasks
- **Git Repository Management**: FastAPI tutorial cookbook clones and manages a Git repository - requires careful handling with ansible.builtin.git module and proper change detection
- **Service Dependencies**: PostgreSQL service must be running before database user creation - requires proper task ordering and handlers in Ansible
- **Multi-site SSL**: Dynamic SSL certificate generation for multiple sites needs to be converted to Ansible loops with community.crypto modules

### Migration Order

1. **cache** (low risk, standalone service) - Start with caching services as they have minimal dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL setup
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- Current Chef cookbooks are actively used in production environments
- SSL certificates are currently self-signed for development/testing purposes - production may require different certificate management approach
- PostgreSQL and Redis passwords are placeholders and will need to be replaced with proper secret management in Ansible (ansible-vault or external secret management)
- The ruby_block configuration fixes in the Redis cookbook suggest compatibility issues that may need different solutions in Ansible
- UFW firewall rules assume standard port configurations (22, 80, 443)
- All target systems have internet access for package installation and Git repository cloning
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Current deployment uses Chef Solo rather than Chef Server, suggesting a simpler migration path to Ansible