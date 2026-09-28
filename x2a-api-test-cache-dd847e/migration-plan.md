# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW firewall, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test/ci/status subdomains), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services layer providing both Redis and Memcached with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom log directory setup, configuration file patching via Ruby blocks, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration specifying cookbook paths and logging settings
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and template-based configuration
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or manual package + template configuration
- **Chef Solo**: Replace with ansible-playbook execution model

### Security Considerations

- **Hardcoded credentials**: Redis password 'redis_secure_password_123' and PostgreSQL password 'fastapi_password' are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider ansible.builtin.openssl_* modules or external CA integration
- **SSH hardening**: Root login disabled, password authentication disabled - preserve in Ansible with ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban configuration**: Template-based jail configuration - migrate to community.general.fail2ban module
- **Sysctl security tuning**: Custom kernel parameters via template - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses Ruby blocks to modify Redis configuration files post-installation - requires conversion to Ansible lineinfile or template-based approach
- **Multi-site nginx configuration**: Dynamic site generation from attributes requires Ansible loops and template variables
- **Service dependency management**: PostgreSQL must be running before database creation, nginx must reload after SSL certificate generation - requires careful task ordering and handlers
- **Git repository management**: FastAPI application deployment via git clone requires ansible.builtin.git module with proper change detection
- **Python virtual environment**: Complex pip installation and virtual environment management needs ansible.builtin.pip module with virtualenv support

### Migration Order

1. **cache** (low risk, foundational service) - Redis and Memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with SSL and security configurations, depends on certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, requires cache and nginx to be functional

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require CA-signed certificates)
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without application code changes
- Vagrant development workflow will be replaced with equivalent Ansible testing approach (molecule or direct VM provisioning)
- Current Chef Solo execution model suggests single-node deployments (no Chef Server infrastructure to migrate)
- Static HTML files in cookbooks/nginx-multisite/files/default/ are simple placeholder content that can be deployed via ansible.builtin.copy
- The Ruby block hack in cache cookbook suggests the redisio cookbook has compatibility issues that may require custom Redis configuration in Ansible
- Network connectivity requirements (HTTP/HTTPS/SSH ports) will remain the same in target environment