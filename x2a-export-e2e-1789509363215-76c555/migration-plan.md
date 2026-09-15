# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW firewall, and system-level security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test/ci/status subdomains), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

**cache**:
- Description: Caching services layer providing both Redis and Memcached with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom log directory setup, configuration file post-processing, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service integration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Vagrant provisioning script

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
- **SSH security hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **System security tuning**: Custom sysctl parameters for security hardening - preserve via ansible.posix.sysctl

### Technical Challenges

- **Redis configuration post-processing**: Chef cookbook includes a Ruby block that manually edits Redis config files to remove specific directives - this hack needs proper Ansible template-based solution
- **Multi-site nginx configuration**: Dynamic site generation based on node attributes requires Ansible template loops and variable management
- **Database initialization**: PostgreSQL user and database creation with proper idempotency checks
- **Service dependencies**: Ensuring proper startup order between PostgreSQL, Redis, and FastAPI application
- **File permissions and ownership**: Multiple services require specific user/group ownership (www-data, redis, postgres)

### Migration Order

1. **cache** (low risk, foundational service) - Redis and Memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security hardening, depends on static file deployment
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service integration

### Assumptions

- SSL certificates are manually managed and placed in /etc/ssl/certs and /etc/ssl/private - certificate provisioning process not defined in current Chef code
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Target environments have internet access for package installation and git repository cloning
- PostgreSQL service configuration beyond basic installation is handled by distribution defaults
- The "cluster.local" domain names are resolvable in the target environment or are placeholder values
- Current Chef Solo execution model will be replaced with Ansible playbook execution
- Development/testing workflow using Vagrant will be replaced with Ansible-compatible local testing approach