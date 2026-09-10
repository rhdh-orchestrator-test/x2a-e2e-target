# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers with Chef and Ansible experience.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, memcached integration, custom Redis config patching, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning for testing cookbook deployment
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning and Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or VM-based deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or custom package/service tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations
- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration with community.crypto collection
- **SSH hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sysctl and ansible.builtin.lineinfile
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban integration**: Custom jail configuration - migrate to community.general.ini_file module
- **File permissions**: SSL private keys with group ssl-cert access - ensure proper file module usage with mode and group settings

### Technical Challenges
- **Redis configuration patching**: Chef uses ruby_block with custom file manipulation to remove specific Redis config lines - requires careful translation to ansible.builtin.lineinfile with state=absent
- **PostgreSQL database initialization**: Chef executes raw SQL commands via sudo -u postgres - migrate to community.postgresql collection modules (postgresql_db, postgresql_user)
- **Systemd service management**: Custom service file creation and daemon-reload - use ansible.builtin.systemd module with daemon_reload parameter
- **Multi-site SSL certificate generation**: Dynamic certificate creation per site - requires Ansible loops with community.crypto.openssl_privatekey and community.crypto.x509_certificate modules
- **Git repository management**: FastAPI app cloning with specific revision - use ansible.builtin.git module with version parameter

### Migration Order
1. **cache** (low risk, standalone caching services with clear dependencies)
2. **nginx-multisite** (moderate complexity, security configurations require careful testing)
3. **fastapi-tutorial** (high complexity, database integration and application deployment dependencies)

### Assumptions
- Target systems will have Python 3 and pip available for Ansible execution
- PostgreSQL service management approach (package vs container) needs clarification
- SSL certificate strategy (self-signed vs Let's Encrypt vs provided certificates) requires decision
- Network connectivity requirements for git repository cloning and package installation need verification
- Service user management strategy (www-data, redis users) may need adjustment based on target OS differences
- Firewall management approach (UFW vs firewalld vs iptables) depends on final target OS selection
- The custom Redis configuration patching logic may indicate underlying compatibility issues that need investigation
- Development vs production environment differences in SSL and security configurations need clarification