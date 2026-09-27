# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, including security hardening, SSL certificate management, and database configuration. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with Redis authentication and Memcached setup, including custom Redis configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached integration, custom configuration patching via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python venv setup, PostgreSQL database and user creation, systemd service management

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban/UFW, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

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
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks

### Security Considerations
- SSH hardening configurations: Migrate PermitRootLogin and PasswordAuthentication settings using ansible.posix.sysctl and lineinfile modules
- UFW firewall rules: Replace with community.general.ufw module
- Fail2ban configuration: Migrate jail.local template to ansible.builtin.template
- SSL certificate management: Self-signed certificates generated via OpenSSL commands need migration to community.crypto.openssl_* modules
- Credential patterns identified:
  - Redis password hardcoded in attributes (redis_secure_password_123)
  - PostgreSQL credentials hardcoded in recipe (fastapi:fastapi_password)
  - Database connection strings in environment files
  - SSL certificate paths and permissions

### Technical Challenges
- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis config files post-installation - requires conversion to ansible.builtin.lineinfile or ansible.builtin.replace tasks
- **Complex template variables**: Nginx site configuration templates use multiple variables that need proper Ansible variable structure
- **Service dependency management**: PostgreSQL must be running before database user creation - requires proper task ordering with ansible.builtin.service
- **File permissions and ownership**: SSL certificates require specific group ownership (ssl-cert) that needs careful migration

### Migration Order
1. **cache** (low risk, moderate complexity) - straightforward service installation with configuration management
2. **fastapi-tutorial** (moderate complexity) - database setup requires careful credential management and service ordering
3. **nginx-multisite** (high complexity) - complex multi-site SSL configuration with security hardening dependencies

### Assumptions
- Target systems will have similar package availability (nginx, postgresql, redis, memcached) as source Ubuntu/CentOS environments
- SSL certificate requirements remain self-signed for development (production may need Let's Encrypt integration)
- Database credentials and Redis passwords will be migrated to Ansible Vault for security
- UFW firewall is acceptable for target environment (may need iptables alternative)
- Systemd is available on target systems for service management
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available
- Python 3 virtual environment approach is suitable for target deployment model
- Current hardcoded paths (/opt/fastapi-tutorial, /var/www/*) are acceptable or will be parameterized
- Fail2ban jail configuration requirements remain consistent across environments