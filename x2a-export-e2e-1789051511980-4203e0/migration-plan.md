# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW firewall, and comprehensive security headers
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL/TLS termination for 3 subdomains (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning, HSTS headers, CSP policies

**cache**:
- Description: Caching services configuration with Redis authentication and Memcached setup for application performance optimization
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis server with password authentication (port 6379), Memcached service, custom Redis configuration cleanup via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Solo runtime**: Replace with Ansible playbook execution via ansible-playbook command

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" in cache cookbook requires migration to Ansible Vault
- **PostgreSQL credentials**: FastAPI database password "fastapi_password" needs Ansible Vault protection
- **SSL certificate management**: Certificate and private key paths configured but certificates not managed by Chef - requires SSL certificate deployment strategy in Ansible
- **SSH security**: Root login disabled and password authentication disabled via template modifications - migrate to ansible.posix.sshd_config module
- **Firewall rules**: UFW configuration with specific port allowances (22, 80, 443) - migrate to community.general.ufw module
- **Security headers**: Comprehensive HTTP security headers in nginx configuration require careful template migration

### Technical Challenges

- **Ruby block workaround**: The cache cookbook contains a ruby_block hack to fix Redis configuration by removing specific lines - this custom logic needs reimplementation in Ansible using lineinfile or template modules
- **Template complexity**: The nginx site.conf.erb template has conditional SSL logic that requires careful Jinja2 template conversion
- **Service dependencies**: PostgreSQL must be running before FastAPI application starts - requires proper Ansible task ordering and handlers
- **Git repository management**: FastAPI cookbook clones from GitHub which may require authentication or repository access validation
- **Multi-site nginx configuration**: Dynamic site generation from attributes requires Ansible loops and template generation

### Migration Order

1. **cache** (Priority 1: Low risk, standalone services)
   - Simple package installation and service management
   - Redis configuration can be templated directly
   - Limited external dependencies

2. **nginx-multisite** (Priority 2: Moderate complexity)
   - Security configurations are well-defined
   - Template conversion is straightforward
   - SSL certificate deployment needs coordination

3. **fastapi-tutorial** (Priority 3: High complexity, multiple dependencies)
   - Requires PostgreSQL, Python environment, Git access
   - Service dependencies and startup ordering critical
   - Database initialization requires careful handling

### Assumptions

- SSL certificates for the three subdomains (test.cluster.local, ci.cluster.local, status.cluster.local) are managed externally and will be available at the specified paths (/etc/ssl/certs and /etc/ssl/private)
- The FastAPI tutorial GitHub repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- Target systems have internet access for package installation and Git repository cloning
- PostgreSQL service can be managed via standard system packages rather than requiring specific version constraints
- The current Chef Solo execution model can be replaced with standard Ansible playbook runs without requiring Chef Server functionality
- UFW firewall rules are appropriate for the target environment and no additional ports need to be opened
- The Redis configuration cleanup hack in the cache cookbook addresses a specific version compatibility issue that may not exist with newer Redis packages
- Development and production environments will use the same Vagrant-based approach or the Vagrantfile can be replaced with appropriate Ansible inventory configuration