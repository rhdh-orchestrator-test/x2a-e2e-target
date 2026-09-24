# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW firewall, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test/ci/status subdomains), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching layer services providing both Redis (with authentication) and Memcached instances for application performance optimization
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, Memcached service, custom Redis configuration cleanup, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, including virtual environment setup and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with cookbook execution order and attribute overrides for site configurations
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Currently commented out, replace with community.crypto.openssl_* modules for certificate management

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - implement proper certificate lifecycle with community.crypto collection
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall rules**: UFW configuration for ports 22, 80, 443 - migrate to community.general.ufw module
- **Fail2ban configuration**: Intrusion prevention system - migrate to community.general.fail2ban module
- **Credential patterns per module**:
  - nginx-multisite: SSL certificate paths, no embedded secrets
  - cache: Redis password hardcoded in attributes
  - fastapi-tutorial: PostgreSQL credentials hardcoded, database connection string in .env file

### Technical Challenges

- **Redis configuration cleanup**: The cache cookbook contains a Ruby block hack to remove specific Redis configuration lines - this custom logic needs careful translation to Ansible lineinfile or template modules
- **Multi-site SSL management**: Dynamic SSL certificate generation for multiple domains requires loop-based certificate creation in Ansible
- **Service dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper service ordering with handlers
- **Python virtual environment**: Chef's execute resources for venv creation and pip installs need conversion to ansible.builtin.pip module with virtualenv parameters
- **Template variable mapping**: ERB templates (.erb) need conversion to Jinja2 (.j2) with variable syntax changes

### Migration Order

1. **cache** (low risk, high value): Simple service installation with clear external dependencies, good starting point to establish patterns
2. **nginx-multisite** (moderate complexity): Core web server functionality, multiple templates and security configurations, foundational for other services
3. **fastapi-tutorial** (high complexity, dependencies): Most complex with database setup, application deployment, and service dependencies on previous modules

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- Current hardcoded passwords are development/testing credentials and will be replaced with proper secret management
- PostgreSQL and Redis services will continue to run on default ports (5432, 6379)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Systemd is available on target systems for service management
- Current UFW firewall rules are sufficient and don't require additional port configurations
- The nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) represent the complete set of required virtual hosts
- Chef Solo execution model can be replaced with Ansible playbook execution without significant workflow changes