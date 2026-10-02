# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating security configurations including fail2ban, UFW firewall, and SSL certificate management.

**Estimated Timeline**: 4-6 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security hardening
**Team Coordination**: Requires coordination between application, infrastructure, and security teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication, custom log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication (redis_secure_password_123), memcached integration, Redis configuration file manipulation via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration, environment file with database credentials

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate auto-generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes - contains site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules for memcached installation and management
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, ansible.builtin.template for redis.conf, and ansible.builtin.service modules

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation for development environments - consider using ansible.builtin.openssl_* modules or community.crypto collection
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate using ansible.builtin.lineinfile for sshd_config
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate using community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate using ansible.builtin.template
- **Sysctl Security Tuning**: Custom security parameters - migrate using ansible.posix.sysctl module
- **Credential Types per Module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation (self-signed for development)

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses a ruby_block to manipulate Redis configuration files with regex replacements - this will need to be converted to Ansible lineinfile or replace modules with appropriate regex patterns
- **Complex Service Dependencies**: FastAPI service depends on PostgreSQL being ready and database/user creation - will require proper task ordering and handlers in Ansible
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple sites based on node attributes - will need Ansible loops and conditional logic
- **Template Variable Mapping**: Chef ERB templates use node attributes that need to be mapped to Ansible variables (e.g., node['nginx']['sites'] becomes nginx_sites)

### Migration Order

1. **cache cookbook** (low risk, standalone caching services)
2. **nginx-multisite cookbook** (moderate complexity, security configurations but no application dependencies)
3. **fastapi-tutorial cookbook** (highest complexity, application deployment with database dependencies)

### Assumptions

- The target environment will maintain the same OS distributions (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments, but production may require proper CA-signed certificates or Let's Encrypt integration
- The current hardcoded passwords are development/testing credentials and will be replaced with proper secret management in production
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible during migration
- UFW firewall is the preferred firewall solution (vs. iptables or firewalld)
- The multi-site configuration pattern (*.cluster.local domains) will be maintained in the Ansible implementation
- PostgreSQL will continue to be used as the database backend for the FastAPI application
- The systemd service management approach for the FastAPI application will be retained
- Redis and memcached will continue to be the caching solutions of choice
- The current nginx configuration patterns and security headers will be preserved