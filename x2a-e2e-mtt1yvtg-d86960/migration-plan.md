# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run_list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning - will need Ansible equivalent for local testing
- `vagrant-provision.sh`: Shell provisioning script - may contain additional setup steps to preserve

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration templates

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to ansible.builtin.openssl_* modules
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **SSH Hardening**: Root login disable, password authentication disable - migrate to ansible.posix.lineinfile or template modules
- **Fail2ban Integration**: Custom jail.local configuration - migrate to community.general.fail2ban module
- **Sysctl Security Tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module
- **Vault/secrets management**: 
  - Hardcoded credentials found in cache cookbook (Redis password: 'redis_secure_password_123')
  - Database credentials in fastapi-tutorial cookbook (PostgreSQL password: 'fastapi_password')
  - SSL certificate paths and configurations in attributes
  - Environment variables in .env file creation
  - All credential references need Ansible Vault integration

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - will need equivalent Ansible lineinfile or replace operations
- **Multi-site SSL Configuration**: Dynamic SSL certificate generation for multiple domains requires loop-based Ansible tasks with proper certificate validation
- **Database Initialization**: PostgreSQL user and database creation with proper privilege assignment needs careful migration to postgresql_* modules
- **Service Dependencies**: Complex service ordering (PostgreSQL before FastAPI, nginx after SSL certificates) requires proper Ansible handlers and task dependencies
- **Template Migration**: ERB templates need conversion to Jinja2 format with equivalent variable substitution

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security configurations, depends on SSL certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service integration

### Assumptions

- Target systems will maintain the same OS family (Ubuntu/CentOS) as specified in cookbook metadata
- SSL certificates can remain self-signed for development environments (production may require Let's Encrypt or CA-signed certificates)
- PostgreSQL and Redis passwords will be migrated to Ansible Vault for security
- The ruby_block configuration fixes in the Redis cookbook indicate potential compatibility issues that may need verification in target environment
- Vagrant development workflow will be preserved with ansible-local provisioner
- The current Chef Solo execution model suggests single-node deployments rather than multi-node orchestration
- Network connectivity requirements (internet access for git clone, package installation) remain unchanged
- File permissions and ownership patterns will be preserved in Ansible equivalent configurations