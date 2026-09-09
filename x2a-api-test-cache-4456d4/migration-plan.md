# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with Redis authentication and Memcached setup, includes Redis log directory management and configuration file patching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached integration, custom Redis configuration fixes via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python venv creation, PostgreSQL database/user provisioning, systemd service configuration

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-domain hosting, security hardening via fail2ban/UFW, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL virtual hosts, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-agnostic configuration

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.template for custom Redis configuration

### Security Considerations
- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall rules**: UFW configuration for ports 22, 80, 443 - migrate to ansible.posix.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate template to Ansible with community.general.fail2ban

### Technical Challenges
- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis config files post-installation - replace with Ansible lineinfile or template modules
- **Complex nginx site management**: Dynamic site creation with SSL certificates requires careful template migration and certificate generation logic
- **Service dependencies**: PostgreSQL must be running before FastAPI application starts - ensure proper Ansible handler and dependency ordering
- **Git repository cloning**: FastAPI cookbook clones from GitHub - ensure network connectivity and consider authentication for private repos

### Migration Order
1. **cache** (low risk, foundational service) - Redis and Memcached are straightforward service installations
2. **fastapi-tutorial** (moderate complexity) - Python application with database dependencies but well-defined workflow
3. **nginx-multisite** (high complexity) - Complex SSL certificate management, multiple virtual hosts, and security configurations

### Assumptions
- Target environments have internet connectivity for package installation and Git repository cloning
- SSL certificates are acceptable as self-signed for development/testing environments
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without application code changes
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- UFW firewall is the preferred firewall solution (vs iptables or firewalld)
- The nginx sites configuration assumes .cluster.local domain resolution is handled externally
- Chef Solo execution model can be replaced with Ansible playbook execution without significant workflow changes