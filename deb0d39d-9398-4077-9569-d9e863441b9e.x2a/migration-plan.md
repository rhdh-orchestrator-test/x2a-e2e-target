# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to SSL certificate management, security hardening, and database configuration. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening (fail2ban, UFW firewall), and system-level security controls including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL certificate generation, multiple virtual hosts with HTTPS redirect, security headers, fail2ban integration, UFW firewall rules, SSH security hardening, sysctl security parameters

**cache**:
- Description: Caching services configuration with Memcached and Redis, including Redis authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication, custom Redis configuration file manipulation, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo configuration with run list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment configuration for testing
- `vagrant-provision.sh`: Vagrant provisioning script for Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Commented out but may be needed - replace with community.crypto.openssl_* modules

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to community.crypto.x509_certificate module with proper certificate lifecycle management
- **Hardcoded Credentials**: 
  - Redis password ('redis_secure_password_123') hardcoded in cache cookbook
  - PostgreSQL credentials ('fastapi_password') hardcoded in fastapi-tutorial cookbook
  - Database connection strings with embedded passwords in environment files
- **SSH Security**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Rules**: UFW configuration with specific port allowances - migrate to community.general.ufw module
- **System Security**: fail2ban configuration and sysctl security parameters - migrate to community.general.fail2ban and ansible.posix.sysctl modules

### Technical Challenges

- **Redis Configuration Manipulation**: The cache cookbook contains a Ruby block that manually edits Redis configuration files to remove specific directives - this complex logic needs to be replicated in Ansible using lineinfile or template modules
- **SSL Certificate Dependencies**: Multiple sites depend on SSL certificates being generated before nginx configuration - requires careful task ordering and proper handlers
- **Database Initialization**: PostgreSQL user and database creation with proper privilege management needs idempotent Ansible tasks
- **Service Dependencies**: FastAPI service depends on PostgreSQL being running - requires proper service ordering and dependency management
- **File Permissions**: Complex SSL certificate file permissions (ssl-cert group, 0710 directories) need careful replication

### Migration Order

1. **cache cookbook** (low risk, high value) - straightforward service installation with known credential management needs
2. **nginx-multisite cookbook** (moderate complexity) - SSL certificate generation and security hardening, but well-defined scope
3. **fastapi-tutorial cookbook** (high complexity, dependencies) - application deployment with database dependencies and systemd service management

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require CA-signed certificates)
- The current hardcoded passwords are acceptable for migration (production should use Ansible Vault)
- The Ruby-based Redis configuration manipulation is still required in the target environment
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible
- Systemd is available on target systems for service management
- The current firewall rules (SSH, HTTP, HTTPS only) meet security requirements
- The fail2ban jail configuration and sysctl security parameters are appropriate for the target environment
- The nginx security headers and SSL configuration meet current security standards