# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with SSL-enabled multi-site hosting, security hardening (fail2ban, UFW firewall), and comprehensive security headers configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL/TLS termination with modern cipher suites, HSTS headers, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning, multiple virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local)

**cache**:
- Description: Caching services configuration with Redis authentication and Memcached setup, including custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis server with password authentication (requirepass), custom log directory creation, configuration file manipulation via Ruby blocks, Memcached integration, depends on external cookbooks

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file generation

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata), recommend standardizing on Red Hat Enterprise Linux 9 for production
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks
- **External cookbook dependencies**: All external Chef Supermarket cookbooks need replacement with equivalent Ansible roles from Ansible Galaxy or custom playbooks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate and private key paths are configured but certificate provisioning method unclear - implement proper certificate management with ansible.builtin.copy or community.crypto modules
- **SSH security configurations**: Root login disabled, password authentication disabled - preserve these security settings in Ansible
- **Firewall rules**: UFW firewall configuration for SSH, HTTP, HTTPS - migrate to ansible.posix.ufw module
- **Security headers**: Comprehensive HTTP security headers in nginx configuration - preserve in Ansible nginx templates
- **Fail2ban configuration**: Intrusion prevention system - migrate to community.general.fail2ban module

### Technical Challenges

- **Ruby block configuration manipulation**: The cache cookbook uses Ruby blocks to modify Redis configuration files post-installation - this will need conversion to Ansible lineinfile or template modules
- **Complex nginx templating**: Multi-site nginx configuration with conditional SSL logic requires careful template migration to Jinja2
- **Service dependencies**: PostgreSQL must be running before database/user creation, nginx must reload after configuration changes - implement proper task ordering and handlers
- **Git repository management**: FastAPI application deployment via git clone needs conversion to ansible.builtin.git module with proper change detection
- **Python virtual environment**: Complex pip installation and virtual environment management needs migration to ansible.builtin.pip module

### Migration Order

1. **cache** (low risk, foundational service) - Redis and Memcached are straightforward service installations
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies
3. **nginx-multisite** (high complexity) - Complex templating, SSL configuration, and security hardening

### Assumptions

- SSL certificates are manually managed or provided externally (certificate generation/renewal process not defined in cookbooks)
- The .cluster.local domains are internal/development domains (no external DNS or certificate authority integration visible)
- PostgreSQL installation uses default package manager versions (no specific version pinning observed)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Current Chef Solo execution model suggests single-node deployments (no multi-node orchestration requirements)
- UFW firewall rules are sufficient for the security model (no complex iptables rules or network segmentation requirements)
- The Ruby block "hack" for Redis configuration indicates potential compatibility issues with the redisio cookbook that may not exist with direct Ansible configuration
- Development/testing currently uses Vagrant, but production deployment method is not specified
- No backup, monitoring, or log rotation configurations are present in the current Chef setup
- The systemd service configuration assumes root user execution for the FastAPI application (may need security review)