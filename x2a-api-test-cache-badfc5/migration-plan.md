# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef Solo configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW, and self-signed certificate generation for development
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion detection, UFW firewall configuration, SSH hardening, sysctl security tuning, custom lineinfile resource

- **cache**:
    - Description: Caching layer with memcached and Redis services, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service via external cookbook, Redis 6379 with password authentication, custom Redis configuration cleanup, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443)
- `vagrant-provision.sh`: Automated Chef installation and Berkshelf dependency resolution script

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for production deployment.
- **Virtual Machine Technology**: libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or private cloud deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration tasks
- **Chef Solo runtime**: Replace with Ansible playbook execution via ansible-playbook command
- **Berkshelf dependency management**: Replace with Ansible Galaxy requirements.yml and ansible-galaxy install

### Security Considerations
- **SSL Certificate Management**: Self-signed certificate generation via OpenSSL commands needs migration to community.crypto.openssl_* modules with proper certificate validation
- **Hardcoded Credentials**: 
  - Redis password 'redis_secure_password_123' in cache/recipes/default.rb - migrate to Ansible Vault
  - PostgreSQL password 'fastapi_password' in fastapi-tutorial/recipes/default.rb - migrate to Ansible Vault
  - Database connection string with embedded credentials in .env file - secure with Ansible Vault
- **SSH Security Configuration**: SSH hardening (disable root login, disable password auth) needs migration to ansible.posix.sshd_config module
- **Firewall Rules**: UFW firewall configuration needs migration to community.general.ufw module
- **Fail2ban Configuration**: Intrusion detection setup needs migration to community.general.fail2ban module
- **File Permissions**: SSL private key permissions (640, ssl-cert group) need careful migration with ansible.builtin.file module

### Technical Challenges
- **Custom Chef Resource**: The lineinfile.rb custom resource needs migration to ansible.builtin.lineinfile module with equivalent functionality
- **Ruby Block Logic**: Complex Ruby logic in cache cookbook for Redis configuration cleanup needs conversion to Ansible tasks with conditional logic
- **Template Variables**: ERB templates need conversion to Jinja2 templates with variable mapping
- **Service Dependencies**: PostgreSQL service dependency for FastAPI application needs proper task ordering with handlers
- **Git Repository Cloning**: GitHub repository cloning with specific revision needs migration to ansible.builtin.git module
- **Python Virtual Environment**: Virtual environment creation and pip dependency installation needs migration to ansible.builtin.pip module with virtualenv support
- **Systemd Service Management**: Custom systemd service file creation needs migration to ansible.builtin.systemd module

### Migration Order
1. **cache cookbook** (low risk, external dependencies) - Start with memcached and Redis services to establish caching layer
2. **fastapi-tutorial cookbook** (moderate complexity) - Migrate Python application with database dependencies
3. **nginx-multisite cookbook** (high complexity, security features) - Final migration with SSL, security hardening, and multi-site configuration

### Assumptions
- Target environment will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development; production deployment will require proper CA-signed certificates
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without service disruption
- libvirt/KVM virtualization platform will be maintained in target environment
- Network configuration (192.168.121.10 private network) can be adapted to target infrastructure
- Chef Solo execution model can be replaced with Ansible playbook runs without architectural changes
- External cookbook dependencies (nginx, memcached, redisio) have equivalent Ansible module functionality
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available during migration
- Systemd service management approach is compatible with target operating system versions
- File ownership and permission model (www-data user/group) can be maintained in Ansible implementation