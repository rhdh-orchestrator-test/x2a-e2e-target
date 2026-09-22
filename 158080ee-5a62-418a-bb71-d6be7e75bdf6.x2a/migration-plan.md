# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation via external cookbook, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate management, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning for testing cookbooks
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package for Redis installation and configuration

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled and password authentication disabled via direct file modification - use ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules managed via shell commands - replace with community.general.ufw module
- **Fail2ban Configuration**: Template-based jail configuration - migrate templates to Jinja2 format
- **Credential Types per Module**:
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded)
  - nginx-multisite: SSL certificate generation (self-signed, no stored credentials)

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or replace modules with proper regex patterns
- **Multi-Site SSL Management**: The nginx-multisite cookbook dynamically generates SSL certificates for each configured site - this logic needs to be converted to Ansible loops with conditional certificate generation
- **Service Dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper service ordering and health checks in Ansible
- **Template Migration**: ERB templates need conversion to Jinja2 format, particularly the nginx.conf.erb and site.conf.erb templates with their Chef-specific variable syntax

### Migration Order

1. **cache** (low risk, standalone service with clear dependencies)
2. **fastapi-tutorial** (moderate complexity, database setup and application deployment)
3. **nginx-multisite** (high complexity, multiple interdependent components, security configurations, and SSL management)

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production deployments may require proper CA-signed certificates)
- The current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault in production)
- The Redis configuration patching workaround in the cache cookbook indicates compatibility issues that may need investigation in the target Redis version
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and compatible
- UFW firewall is the preferred firewall solution for the target environment
- The three configured sites (test.cluster.local, ci.cluster.local, status.cluster.local) represent the complete set of required virtual hosts
- Systemd is available on target systems for service management
- The current Chef Solo deployment model suggests a single-node or small-scale deployment that doesn't require complex orchestration