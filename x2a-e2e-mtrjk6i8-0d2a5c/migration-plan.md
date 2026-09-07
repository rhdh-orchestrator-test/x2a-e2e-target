# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and an nginx multi-site reverse proxy with security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis 6379, including Redis authentication, log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication (redis_secure_password_123), memcached integration, Redis log directory management, configuration file post-processing

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site-specific settings and security parameters
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible conversion)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified (local development environment focus)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation for development environments - consider Let's Encrypt integration for production
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve in Ansible with ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **System Security**: Sysctl security tuning via templates - migrate to ansible.posix.sysctl module
- **Fail2ban Integration**: Jail configuration for nginx protection - migrate to community.general.fail2ban module
- **Credential Types per Module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation (self-signed)

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that post-processes Redis configuration files to remove specific directives - this will need custom Ansible tasks with lineinfile or replace modules
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple domains requires loop-based certificate creation in Ansible
- **Service Dependencies**: PostgreSQL must be running before database/user creation, nginx must reload after configuration changes - ensure proper task ordering and handlers
- **Template Migration**: ERB templates (.erb) need conversion to Jinja2 (.j2) format with syntax adjustments
- **Package Management**: Multi-platform support (Ubuntu/CentOS) requires conditional package installation based on ansible_os_family

### Migration Order

1. **cache** (low risk, standalone caching services)
2. **nginx-multisite** (moderate complexity, security configurations but no external service dependencies)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions

- The current Chef configuration is working in the target environment and all external dependencies are available
- SSL certificates are self-signed for development purposes; production deployment may require different certificate management
- The PostgreSQL and Redis services are intended to run on the same host as the applications
- The UFW firewall configuration is appropriate for the target environment's security requirements
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) is accessible and contains a valid requirements.txt file
- The systemd service configuration for FastAPI is suitable for the target deployment environment
- All hardcoded passwords are development/testing credentials and will be replaced with proper secret management in production