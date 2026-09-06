# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef Solo configuration that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL termination, multi-site configuration, security hardening (fail2ban, UFW firewall), and self-signed certificate generation for development
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: SSL-enabled virtual hosts for test.cluster.local, ci.cluster.local, status.cluster.local; fail2ban intrusion prevention; UFW firewall configuration; SSH hardening; sysctl security tuning; custom lineinfile resource

- **cache**:
    - Description: Caching services configuration with Memcached and Redis, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service setup; Redis 6379 with password authentication (redis_secure_password_123); custom Ruby block to fix Redis configuration issues; log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 virtual environment; Git repository cloning from https://github.com/dibanez/fastapi_tutorial.git; PostgreSQL database and user creation; systemd service management; environment configuration with database credentials

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes including site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443), and rsync folder sync
- `vagrant-provision.sh`: Automated provisioning script that installs Chef, Berkshelf, downloads dependencies, and runs Chef Solo

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata supports declarations). Default to Red Hat Enterprise Linux 9 for standardization.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or local development environment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or manual configuration with ansible.builtin.template
- **Chef Solo runtime**: Replace with Ansible playbook execution
- **Berkshelf dependency management**: Replace with Ansible Galaxy requirements.yml and ansible-galaxy install

### Security Considerations
- **Hardcoded Redis password**: The Redis password "redis_secure_password_123" is hardcoded in cookbooks/cache/recipes/default.rb and needs to be moved to Ansible Vault
- **PostgreSQL credentials**: Database password "fastapi_password" is hardcoded in cookbooks/fastapi-tutorial/recipes/default.rb and requires Ansible Vault protection
- **SSL certificate management**: Self-signed certificates are generated automatically - consider implementing proper certificate management with Let's Encrypt or internal CA
- **SSH hardening configurations**: Root login disabled, password authentication disabled - ensure these security settings are preserved in Ansible
- **Firewall rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS) must be replicated
- **Fail2ban intrusion prevention**: Jail configuration needs to be migrated to Ansible
- **Sysctl security tuning**: Kernel parameter hardening configurations need preservation

### Technical Challenges
- **Custom Ruby resource (lineinfile)**: The nginx-multisite cookbook includes a custom Chef resource for line-in-file operations that needs to be replaced with ansible.builtin.lineinfile module
- **Redis configuration fixes**: The cache cookbook contains a Ruby block that performs regex-based configuration file manipulation to remove problematic Redis settings - this logic needs to be replicated in Ansible
- **Complex template variables**: Multiple ERB templates with site-specific variables need conversion to Jinja2 templates
- **Service dependency management**: PostgreSQL must be running before FastAPI application starts - requires proper Ansible handler and dependency ordering
- **Git repository cloning with specific revision**: FastAPI cookbook clones from GitHub main branch - ensure Ansible git module handles this correctly
- **Python virtual environment management**: Complex pip installation within venv requires careful Ansible pip module configuration
- **Systemd service file generation**: Dynamic service file creation needs to be replicated with ansible.builtin.template

### Migration Order
1. **cache cookbook** (low risk, minimal dependencies) - Start with caching services as they have fewer interdependencies
2. **fastapi-tutorial cookbook** (moderate complexity) - Migrate application deployment after cache services are stable
3. **nginx-multisite cookbook** (high complexity, multiple dependencies) - Final migration as it depends on other services and has the most complex security configurations

### Assumptions
- The target environment will maintain the same network configuration (192.168.121.10 IP address) or network settings will be updated accordingly
- The three domain names (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same or DNS/hosts file updates will be handled separately
- The FastAPI tutorial GitHub repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and the main branch will be stable
- PostgreSQL and Redis authentication requirements will remain the same, but passwords will be properly secured in Ansible Vault
- The target systems will have internet access for package installation and Git repository cloning
- The libvirt/KVM virtualization platform will be maintained, or the migration will include updating to the target virtualization platform
- SSL certificate requirements may evolve from self-signed certificates to proper CA-signed certificates
- The development/testing workflow using Vagrant may be replaced with alternative testing approaches (containers, cloud instances, etc.)
- System package managers (apt for Ubuntu, yum/dnf for RHEL/CentOS) will be available and configured
- The target Ansible control node will have necessary collections installed (community.general, community.postgresql, etc.)
- File permissions and ownership requirements will remain consistent between Chef and Ansible implementations
- The systemd service manager will be available on target systems for service management
- Network firewall policies will allow the same port access patterns (22, 80, 443, 6379, 5432, 8000)