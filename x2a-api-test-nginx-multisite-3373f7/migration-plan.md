# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external cookbook dependencies, and migrating security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication, custom log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom log directory creation, configuration file post-processing

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service management, environment file configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL configuration, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and node configuration
- `Vagrantfile`: Development environment provisioning - will need Ansible equivalent for local testing
- `vagrant-provision.sh`: Shell provisioning script - should be replaced with Ansible playbook execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Ansible tasks for Redis installation and configuration

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH hardening**: Root login disable and password authentication disable configured via sed commands - migrate to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules managed via shell commands - migrate to community.general.ufw module
- **Fail2ban configuration**: Template-based jail configuration - migrate to ansible.builtin.template with Jinja2 templates
- **Credential patterns per module**:
  - cache: Redis password in node attributes
  - fastapi-tutorial: PostgreSQL credentials in execute blocks and environment files
  - nginx-multisite: SSL certificate generation with embedded subject information

### Technical Challenges

- **Redis configuration patching**: The cache cookbook uses a Ruby block to post-process Redis configuration files by removing specific lines - this will need to be replicated using ansible.builtin.lineinfile with state=absent
- **Multi-site SSL certificate generation**: Dynamic certificate generation for multiple domains based on node attributes - will require Ansible loops with community.crypto modules
- **PostgreSQL database initialization**: Chef execute blocks for database and user creation - migrate to community.postgresql.postgresql_db and community.postgresql.postgresql_user modules
- **Systemd service file templating**: Inline service file content in Chef file resources - migrate to ansible.builtin.template with separate service file templates
- **Attribute-driven site configuration**: Dynamic nginx site configuration based on node['nginx']['sites'] hash - will require Ansible variable structures and template loops

### Migration Order

1. **cache** (low risk, high value) - Straightforward service installation with well-defined external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database setup, manageable scope
3. **nginx-multisite** (high complexity, dependencies) - Complex multi-site SSL configuration with security hardening, depends on understanding of target site requirements

### Assumptions

- Target environments will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+)
- Self-signed certificates are acceptable for the target environment (production may require CA-signed certificates)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and compatible
- Current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault in production)
- UFW firewall is the preferred firewall solution for the target environment
- PostgreSQL will remain the database backend for the FastAPI application
- Redis and memcached versions available in target OS repositories are compatible with application requirements
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the actual target deployment requirements
- Vagrant-based development workflow will be maintained or replaced with equivalent Ansible-based local testing