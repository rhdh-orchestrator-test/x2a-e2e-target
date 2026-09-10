# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW firewall, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test/ci/status subdomains), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services layer providing both Redis (with authentication) and Memcached instances for application performance optimization
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis server with password authentication, Memcached service, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, including virtual environment setup and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration specifying cookbook paths and logging
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Shell script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic with local development focus

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management
- **Chef Solo**: Replace with Ansible playbooks and inventory management

### Security Considerations

- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipe code - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - maintain equivalent iptables or firewalld rules
- **Fail2ban integration**: Intrusion prevention configured - ensure equivalent protection in Ansible
- **Credential types per module**:
  - nginx-multisite: SSL certificate paths, no embedded secrets
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded), application environment variables

### Technical Challenges

- **Redis configuration patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this custom logic needs careful translation to Ansible lineinfile or template modules
- **Multi-site SSL management**: Dynamic SSL certificate generation and nginx site configuration based on node attributes requires Ansible loops and conditional logic
- **Service orchestration**: Complex service dependencies (PostgreSQL → FastAPI → Nginx) need proper Ansible task ordering and handlers
- **Template migration**: ERB templates (.erb files) need conversion to Jinja2 format for Ansible
- **Attribute-driven configuration**: Chef's node attributes system needs mapping to Ansible variables and group_vars structure

### Migration Order

1. **cache** (low risk, foundational service) - Redis and Memcached services with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies
3. **nginx-multisite** (high complexity) - Reverse proxy configuration dependent on backend services, complex SSL and security configurations

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require proper CA-signed certificates)
- Current hardcoded passwords are development/testing credentials and will be replaced with proper secret management
- The Vagrant development environment setup will be replaced with equivalent Ansible testing infrastructure
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with community Ansible collections
- The Chef Solo execution model will translate to Ansible playbook execution without significant architectural changes
- Network topology and firewall requirements remain consistent with current UFW rule definitions
- PostgreSQL and Redis service configurations are compatible with target OS package manager versions