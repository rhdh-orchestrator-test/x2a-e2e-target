# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW firewall, and system-level security configurations including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test/ci/status subdomains), fail2ban intrusion prevention, UFW firewall rules, SSH security hardening, sysctl kernel security parameters

**cache**:
- Description: Caching services layer providing both Redis and Memcached with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom log directory management, configuration file post-processing via ruby_block, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service integration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Bootstrap script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and ansible.builtin.template for configuration
- **Chef Solo**: Replace with Ansible playbook execution model

### Security Considerations

- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipe code - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths defined in attributes (/etc/ssl/certs, /etc/ssl/private) - implement proper certificate deployment with Ansible Vault for private keys
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security configurations in Ansible
- **Firewall configuration**: UFW rules for SSH/HTTP/HTTPS - migrate to ansible.posix.ufw module
- **System security**: fail2ban and sysctl security parameters - migrate to respective Ansible modules
- **Database credentials**: PostgreSQL user creation with embedded passwords - migrate to ansible.builtin.postgresql_* modules with Ansible Vault

### Technical Challenges

- **Ruby block configuration hacks**: The cache cookbook uses ruby_block to post-process Redis configuration files - requires custom Ansible tasks with ansible.builtin.lineinfile or ansible.builtin.replace modules
- **Multi-site nginx configuration**: Template-driven virtual host generation needs conversion to Jinja2 templates with proper loop structures
- **Service dependencies**: Complex service startup order (PostgreSQL before FastAPI, nginx after SSL setup) requires careful Ansible handler and dependency management
- **Git repository management**: FastAPI application deployment via git clone needs conversion to ansible.builtin.git module with proper change detection
- **Python virtual environment**: Complex pip installation and venv management requires ansible.builtin.pip module with virtualenv parameters

### Migration Order

1. **cache** (low risk, foundational service) - Redis and Memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security hardening, depends on SSL certificate deployment strategy
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, git integration, and service management

### Assumptions

- SSL certificates are manually deployed or managed externally (no certificate generation logic found in cookbooks)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Current Chef Solo execution model can be replaced with Ansible playbook runs without workflow disruption
- Database initialization and schema management is handled by the FastAPI application itself (no database migration scripts found)
- The three subdomain sites (test.cluster.local, ci.cluster.local, status.cluster.local) serve static content only (based on simple index.html files)
- Network connectivity and DNS resolution for the cluster.local domain is configured externally
- The ruby_block configuration hack in the Redis setup indicates potential compatibility issues with the redisio cookbook that may not exist with direct Ansible Redis configuration