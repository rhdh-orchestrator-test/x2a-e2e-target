# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Redis and Memcached caching services with authentication, custom configuration patching, and log directory management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config file patching via ruby_block, log directory creation

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening (fail2ban, UFW firewall), and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site nginx configuration, SSL certificate generation, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package for Redis installation and configuration

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using ansible.builtin.openssl_* modules or community.crypto collection
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate using ansible.builtin.lineinfile for sshd_config
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate using community.general.ufw module
- **Fail2ban Configuration**: Intrusion prevention with custom jail.local template - migrate using ansible.builtin.template
- **Credential Types per Module**:
  - cache: Redis authentication password (1 credential)
  - fastapi-tutorial: PostgreSQL database password, application environment variables (2 credentials)
  - nginx-multisite: SSL certificate generation (no stored credentials, but certificate management)

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses a ruby_block to patch Redis configuration files with regex replacements - this custom logic needs to be replicated using ansible.builtin.replace or ansible.builtin.lineinfile modules
- **Complex Service Dependencies**: FastAPI service depends on PostgreSQL being ready and database/user creation - requires careful task ordering and wait conditions in Ansible
- **Template Variable Mapping**: Chef ERB templates use node attributes that need to be mapped to Ansible variables (e.g., node['nginx']['sites'] to ansible variables)
- **Multi-Site SSL Generation**: Dynamic SSL certificate generation for multiple sites requires Ansible loops and conditional logic
- **Git Repository Management**: FastAPI cookbook clones and syncs git repositories - migrate to ansible.builtin.git module with proper change detection

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational infrastructure)
2. **cache** (low-moderate complexity, independent services)
3. **fastapi-tutorial** (highest complexity, depends on database setup and application deployment)

### Assumptions

- Target systems will maintain the same OS family (Ubuntu/CentOS) as specified in cookbook metadata
- SSL certificates can remain self-signed for development environments, or external certificate management will be implemented separately
- PostgreSQL and Redis services will continue to run on the same hosts as the applications
- The Vagrant development environment will be replaced with an equivalent Ansible-based development setup
- Network connectivity and firewall rules (UFW) requirements will remain the same
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and compatible
- Python virtual environment approach will be maintained rather than switching to containerization
- Systemd service management approach will be preserved for the FastAPI application
- Current backup and monitoring strategies (if any) are handled outside of this configuration management scope