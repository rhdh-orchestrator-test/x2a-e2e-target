# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW firewall, and system-level security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test/ci/status subdomains), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

**cache**:
- Description: Caching services layer providing both Redis and Memcached with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom log directory setup, configuration file manipulation via Ruby blocks, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, virtual environment management, and systemd service integration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Vagrant provisioning script for Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and template-based configuration
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations
- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths defined but certificate provisioning not automated - implement proper certificate management workflow
- **SSH security hardening**: Root login disabled, password authentication disabled - preserve these security controls in Ansible
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **System security tuning**: Custom sysctl parameters for security hardening - migrate to ansible.posix.sysctl module
- **Credential types per module**:
  - nginx-multisite: SSH configuration, SSL certificate references
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables

### Technical Challenges
- **Ruby block configuration manipulation**: The cache cookbook uses Ruby blocks to modify Redis configuration files post-installation - requires custom Ansible tasks with lineinfile or replace modules
- **Multi-site nginx configuration**: Complex template-driven virtual host setup with SSL - migrate to Jinja2 templates with proper variable structure
- **Service orchestration**: Dependencies between PostgreSQL, Redis, and application services - implement proper task ordering and handlers
- **Git repository management**: FastAPI application deployment via git clone - migrate to ansible.builtin.git module with proper change detection
- **Python virtual environment**: Complex pip installation within venv - use ansible.builtin.pip with virtualenv parameters

### Migration Order
1. **cache** (low risk, foundational service) - Redis and Memcached setup with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security hardening, depends on cache services for optimal performance
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, should be migrated after infrastructure is stable

### Assumptions
- SSL certificates are manually managed and placed in /etc/ssl/certs and /etc/ssl/private - certificate provisioning process needs clarification
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable during migration
- PostgreSQL installation uses distribution packages rather than custom compilation or specific version requirements
- The target environment has internet access for package installation and git repository cloning
- Current Chef Solo execution model suggests single-node deployments - multi-node orchestration requirements are unclear
- UFW firewall rules assume standard port usage (22/SSH, 80/HTTP, 443/HTTPS) - custom port requirements not specified
- Redis configuration manipulation via Ruby blocks suggests specific version compatibility issues that may not apply to Ansible-managed installations
- Development workflow relies on Vagrant - equivalent Ansible testing environment needs establishment