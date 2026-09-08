# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external cookbook dependencies, and migrating security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers with moderate Chef/Ansible experience.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database/user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-domain hosting, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook versions (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with site-specific attributes and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and logging
- `Vagrantfile`: Development environment provisioning - will need Ansible equivalent
- `vagrant-provision.sh`: Shell provisioning script - analyze for additional setup requirements

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible-role-nginx or community.general.nginx modules
- **memcached (~> 6.0)**: Replace with community.general.memcached or custom Ansible tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis or geerlingguy.redis role

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation for development environments - consider Let's Encrypt integration for production
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve in Ansible with ansible.posix.sshd_config
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Integration**: Jail configuration for nginx protection - use community.general.fail2ban role
- **Sysctl Security Tuning**: Kernel parameter hardening - use ansible.posix.sysctl module

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses ruby_block to patch Redis configuration files post-installation - will need equivalent Ansible lineinfile/replace tasks
- **Complex Service Dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper Ansible handlers and service ordering
- **Multi-Site SSL Generation**: Dynamic SSL certificate creation per site - use Ansible loops with openssl_certificate module
- **Template Migration**: Convert ERB templates (nginx.conf.erb, security.conf.erb, etc.) to Jinja2 format
- **Attribute Override Complexity**: solo.json overrides cookbook attributes - migrate to Ansible group_vars/host_vars structure

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web infrastructure)
2. **cache** (low complexity, independent caching services)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions

- Current deployment uses Chef Solo rather than Chef Server/Client architecture
- SSL certificates are self-signed for development - production certificates managed separately
- PostgreSQL and Redis services run on the same host as the web application
- UFW is the preferred firewall solution over iptables
- Systemd is available for service management (Ubuntu 18.04+/CentOS 7+ requirement)
- Git repository access for FastAPI tutorial code is available during deployment
- Python 3 virtual environments are the preferred isolation method over system packages
- The 'ssl-cert' group exists or can be created for SSL key file permissions
- Fail2ban configuration is standardized across environments
- No external Chef Server integration or encrypted data bags are in use