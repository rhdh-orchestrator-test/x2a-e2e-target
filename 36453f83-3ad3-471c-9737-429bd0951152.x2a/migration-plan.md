# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure setup that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI tutorial application with PostgreSQL backend. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external cookbook dependencies, and migrating security configurations including fail2ban, UFW firewall, and SSL certificate management.

**Migration Complexity**: Medium-High  
**Estimated Timeline**: 3-4 weeks  
**Team Coordination Required**: DevOps, Security, and Application teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban and UFW firewall, self-signed certificate generation, and comprehensive security headers
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: SSL/TLS termination with HTTP to HTTPS redirects, fail2ban intrusion prevention, UFW firewall rules, sysctl security tuning, SSH hardening, custom lineinfile resource, security headers (HSTS, CSP, X-Frame-Options)

- **cache**:
    - Description: Caching layer configuration with Redis authentication and Memcached, including custom Redis configuration fixes and log directory management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication (redis_secure_password_123), Memcached service, custom Redis config file manipulation, log directory creation with proper ownership

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file creation

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies from Chef Supermarket (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes including nginx site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `vagrant-provision.sh`: Vagrant provisioning script that installs Chef, Berkshelf, downloads dependencies, and runs Chef Solo
- `Vagrantfile`: Vagrant VM configuration (not examined but present in repository)

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from vagrant-provision.sh and Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx installation and configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package for Redis installation and configuration
- **Chef Supermarket cookbooks**: All external cookbook dependencies need to be replaced with equivalent Ansible modules or community collections

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands needs migration to ansible.builtin.openssl_* modules or community.crypto collection
- **Firewall Configuration**: UFW firewall rules need migration to community.general.ufw module
- **SSH Hardening**: SSH configuration changes need migration to ansible.builtin.lineinfile or ansible.posix.sshd_config modules
- **Fail2ban Configuration**: Template-based fail2ban configuration needs migration to ansible.builtin.template module
- **Vault/secrets management**: 
  - **cache module**: 1 hardcoded Redis password (redis_secure_password_123) in recipes/default.rb
  - **fastapi-tutorial module**: 2 hardcoded credentials (PostgreSQL user password 'fastapi_password' and database connection string) in recipes/default.rb
  - **nginx-multisite module**: No hardcoded credentials detected, uses certificate paths from attributes
  - **Total credentials detected**: 3 hardcoded passwords requiring Ansible Vault migration

### Technical Challenges

- **Custom Chef Resource Migration**: The custom `lineinfile` resource in nginx-multisite/resources/lineinfile.rb needs to be replaced with ansible.builtin.lineinfile module, requiring logic translation from Ruby to YAML
- **Ruby Block Logic**: Complex Ruby blocks in cache/recipes/default.rb for Redis configuration file manipulation need conversion to Ansible tasks using ansible.builtin.replace or ansible.builtin.lineinfile modules
- **Template Variable Mapping**: ERB templates need conversion to Jinja2 templates with variable name mapping (e.g., @server_name to {{ server_name }})
- **Service Dependency Management**: Chef's `notifies` and `subscribes` patterns need conversion to Ansible handlers and task dependencies
- **Package Installation Coordination**: Multiple cookbooks installing overlapping packages need coordination to avoid conflicts in Ansible playbooks

### Migration Order

1. **cache** (Priority 1 - low risk, foundational service)
   - Simple package installation with minimal external dependencies
   - Provides caching services needed by other applications
   
2. **fastapi-tutorial** (Priority 2 - moderate complexity)
   - Self-contained application with database setup
   - No dependencies on other cookbooks
   
3. **nginx-multisite** (Priority 3 - high complexity, security critical)
   - Complex security configurations and SSL management
   - Multiple recipe dependencies and custom resources
   - Critical for web service availability

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+ and CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production environments may require CA-signed certificates)
- The Vagrant-based development workflow will be replaced with Ansible-based provisioning
- External cookbook dependencies from Chef Supermarket have equivalent functionality available in Ansible Galaxy collections
- The current hardcoded passwords in cache and fastapi-tutorial cookbooks are acceptable for development but will need proper secret management in production
- The custom lineinfile resource functionality can be adequately replaced with Ansible's built-in lineinfile module
- The Ruby-based configuration file manipulation in the cache cookbook can be converted to equivalent Ansible tasks
- Network configuration and firewall rules (UFW) are appropriate for the target deployment environment
- PostgreSQL and Redis authentication mechanisms will remain the same in the Ansible implementation
- The systemd service management approach in fastapi-tutorial cookbook is compatible with target systems
- SSL/TLS cipher suites and security headers configured in nginx templates meet current security requirements