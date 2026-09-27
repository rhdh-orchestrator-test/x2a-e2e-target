# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a Python FastAPI application. The migration involves converting Chef cookbooks to Ansible roles, replacing external cookbook dependencies with Ansible collections, and adapting Chef-specific patterns to Ansible best practices. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL certificates (self-signed), fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes - contains site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning for testing
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.posix.firewalld and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with community.general.memcached module and package management
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban Integration**: Custom jail configuration for nginx protection - migrate templates to Ansible
- **Credential Types per Module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation, no stored credentials but security configurations

### Technical Challenges

- **Chef Ruby Blocks**: The cache cookbook contains Ruby code for Redis configuration patching - requires conversion to Ansible lineinfile or replace modules
- **Template Migration**: ERB templates (.erb) need conversion to Jinja2 (.j2) format with syntax adaptation
- **Service Dependencies**: Complex service ordering (PostgreSQL before FastAPI, nginx after SSL setup) needs careful Ansible handler and dependency management
- **Git Repository Management**: FastAPI cookbook clones and manages Git repositories - migrate to ansible.builtin.git module
- **Self-signed Certificate Generation**: OpenSSL certificate generation logic needs adaptation to Ansible crypto modules

### Migration Order

1. **nginx-multisite** (foundational infrastructure, moderate complexity)
2. **cache** (independent caching services, contains Ruby block complexity)
3. **fastapi-tutorial** (application layer, depends on database setup)

### Assumptions

- Current Chef Solo execution model will be replaced with Ansible playbook execution
- Vagrant development environment will be maintained for testing migrated Ansible roles
- SSL certificates are currently self-signed for development - production certificate management strategy needs clarification
- Database credentials and Redis passwords will be externalized to Ansible Vault during migration
- UFW firewall is the preferred firewall solution (vs. iptables or firewalld)
- The target environment supports systemd for service management
- Git repository access for FastAPI tutorial code is available and doesn't require authentication
- Current Chef cookbook version constraints can be mapped to equivalent Ansible collection versions
- The migration will maintain the same multi-site nginx configuration pattern with separate document roots per domain