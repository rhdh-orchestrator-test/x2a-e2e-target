# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and preserving security configurations. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Multi-site nginx web server with SSL termination, security hardening (fail2ban, UFW firewall), and custom site configurations for test.cluster.local, ci.cluster.local, and status.cluster.local
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Self-signed SSL certificate generation, fail2ban intrusion prevention, UFW firewall configuration, SSH hardening (disable root login, disable password auth), sysctl security tuning, custom lineinfile resource for configuration management

- **cache**:
    - Description: Caching layer configuration with memcached and Redis services, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service setup, Redis with password authentication (redis_secure_password_123), custom Redis configuration cleanup via ruby_block, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from https://github.com/dibanez/fastapi_tutorial.git, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook references
- `solo.json`: Chef Solo run list and node attributes defining nginx sites, SSL configuration, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, network configuration (192.168.121.10), and port forwarding (80→8080, 443→8443)
- `vagrant-provision.sh`: Automated Chef installation and cookbook dependency resolution using Berkshelf

### Target Details

- **Operating System**: Based on cookbook metadata supporting Ubuntu >= 18.04 and CentOS >= 7.0, with Vagrant using Fedora 42. Target should be Ubuntu 20.04 LTS or RHEL 8/9 for production compatibility.
- **Virtual Machine Technology**: Vagrant configuration specifies libvirt provider with 2GB RAM and 2 CPUs for development environment.
- **Cloud Platform**: Not specified - appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **berkshelf**: Replace with ansible-galaxy for role dependency management
- **chef-solo**: Replace with ansible-playbook execution

### Security Considerations
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands need migration to ansible.builtin.openssl_* modules or community.crypto collection
- **Firewall Configuration**: UFW commands need migration to community.general.ufw module
- **SSH Hardening**: Direct file modifications to /etc/ssh/sshd_config need migration to ansible.posix.sshd_config module
- **Fail2ban Configuration**: Template-based jail.local configuration needs migration to community.general.fail2ban module
- **Vault/secrets management**: 
  - **nginx-multisite**: No hardcoded credentials detected, SSL certificates are self-generated
  - **cache**: 1 hardcoded Redis password ('redis_secure_password_123') in default recipe - needs Ansible Vault encryption
  - **fastapi-tutorial**: 2 hardcoded credentials detected - PostgreSQL password ('fastapi_password') and database connection string in .env file - both need Ansible Vault encryption

### Technical Challenges
- **Custom Chef Resource Migration**: The lineinfile.rb custom resource needs replacement with ansible.builtin.lineinfile module, requiring logic translation from Ruby to YAML
- **Ruby Block Logic**: Complex Ruby blocks in cache cookbook for Redis configuration cleanup need conversion to Ansible tasks using ansible.builtin.replace or ansible.builtin.lineinfile modules
- **Template Variable Mapping**: ERB templates (.erb files) need conversion to Jinja2 templates (.j2) with variable syntax changes (e.g., <%= node['attr'] %> to {{ ansible_variable }})
- **Service Notification Patterns**: Chef's notifies/subscribes pattern needs mapping to Ansible handlers and notify/listen mechanisms
- **Git Repository Cloning**: Chef git resource needs migration to ansible.builtin.git module with equivalent revision and sync behavior
- **PostgreSQL Database Management**: Chef execute blocks for database creation need migration to community.postgresql.postgresql_* modules

### Migration Order
1. **cache** (low risk, high value) - Simple service installation with clear external dependencies, minimal custom logic
2. **nginx-multisite** (moderate complexity) - Core web server functionality with security features, custom resource requires careful migration
3. **fastapi-tutorial** (high complexity, dependencies) - Application deployment with database dependencies, systemd service management, and environment configuration

### Assumptions
- Target systems will have Python 3.8+ available for Ansible execution
- PostgreSQL version compatibility maintained between Chef and Ansible deployments
- Self-signed SSL certificates are acceptable for development/testing environments (production may require Let's Encrypt or CA-signed certificates)
- UFW firewall is the preferred firewall solution (vs. firewalld on RHEL systems)
- Systemd is available on target systems for service management
- Git repository https://github.com/dibanez/fastapi_tutorial.git remains accessible and stable
- Redis and memcached versions from distribution packages are acceptable (vs. specific versions from Chef cookbooks)
- Network configuration (192.168.121.10) is development-specific and will need adjustment for production environments
- Chef cookbook dependencies (nginx, memcached, redisio) provide equivalent functionality to Ansible modules and may require feature gap analysis
- File ownership and permissions (www-data user/group) are consistent between Chef and Ansible target systems
- Berkshelf vendoring behavior can be replicated with ansible-galaxy role installation and requirements.yml management