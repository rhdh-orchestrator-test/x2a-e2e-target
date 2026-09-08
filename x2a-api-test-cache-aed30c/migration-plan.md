# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, including SSL certificate management, security hardening, and database configuration. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with Redis authentication and Memcached setup, includes Redis log directory management and configuration file patching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached integration, custom Redis configuration fixes via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python venv setup, PostgreSQL database and user creation, systemd service management

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL sites configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with site-specific attributes and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations
- SSL certificate management: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules
- Hardcoded credentials in recipes:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL credentials: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection strings in .env files
- SSH security configurations: Root login disable, password authentication disable
- Firewall rules: UFW configuration with specific port allowances
- Fail2ban jail configuration for nginx protection
- Sysctl security parameter tuning

### Technical Challenges
- Ruby block configuration patching: The cache cookbook uses ruby_block to modify Redis config files post-installation, requiring custom Ansible tasks or lineinfile modules
- Complex nginx site templating: Multi-site SSL configuration with dynamic certificate paths needs careful Jinja2 template conversion
- Service dependency management: PostgreSQL must be running before database user creation, requiring proper task ordering
- Git repository cloning with specific revision handling for FastAPI application deployment

### Migration Order
1. **cache** (low risk, moderate complexity) - Straightforward service installation with configuration management
2. **fastapi-tutorial** (moderate complexity) - Database setup and Python application deployment
3. **nginx-multisite** (high complexity) - Complex multi-site SSL configuration with security hardening

### Assumptions
- Target systems will have internet access for package installation and git repository cloning
- SSL certificates are self-signed for development/testing (production may require Let's Encrypt or CA-signed certificates)
- PostgreSQL and Redis services will run on the same host as the web application
- UFW firewall is the preferred firewall solution (may need adaptation for RHEL/CentOS systems using firewalld)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Current Chef Solo deployment model will be replaced with Ansible playbook execution
- Existing attribute-based configuration in solo.json will be converted to Ansible variables/group_vars structure