# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and custom site templates for test, CI, and status subdomains
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts, fail2ban intrusion prevention, UFW firewall rules, sysctl security tuning, SSH hardening, custom site configurations for cluster.local domains

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service setup, Redis with password authentication, custom Redis configuration patching via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or VM-based deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations
- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths configured but certificate provisioning not automated - implement proper certificate management with ansible.builtin.copy or community.crypto modules
- **SSH hardening**: Root login disabled and password authentication disabled via sed commands - convert to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules managed via execute resources - migrate to community.general.ufw module
- **Fail2ban configuration**: Template-based jail configuration - convert to ansible.builtin.template with proper handlers
- **Credential types per module**:
  - nginx-multisite: SSL certificate references, no embedded passwords
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database password (hardcoded), application environment variables

### Technical Challenges
- **Ruby block configuration patching**: The cache cookbook uses a ruby_block to modify Redis configuration files post-installation - requires conversion to ansible.builtin.lineinfile or ansible.builtin.replace modules with proper regex patterns
- **Multi-site nginx configuration**: Complex template-driven virtual host setup with dynamic site creation - needs conversion to Ansible loops with ansible.builtin.template module
- **Service dependency management**: PostgreSQL must be running before FastAPI application starts - implement proper task ordering and handlers in Ansible
- **Git repository management**: FastAPI cookbook clones and syncs git repositories - migrate to ansible.builtin.git module with proper change detection

### Migration Order
1. **cache** (low risk, standalone service with clear dependencies)
2. **fastapi-tutorial** (moderate complexity, database dependencies but isolated application)
3. **nginx-multisite** (high complexity, security configurations and multi-site templates)

### Assumptions
- SSL certificates will be provided externally or managed through a separate certificate management process (current implementation only configures paths)
- The cluster.local domain structure will be maintained in the target environment
- PostgreSQL and Redis services will continue to run on the same hosts as the applications
- The current Chef Solo deployment model will be replaced with Ansible playbook execution
- Development environment provisioning via Vagrant is optional and may be replaced with alternative local development approaches
- External cookbook dependencies (nginx, memcached, redisio) functionality will be replicated using native Ansible modules rather than community cookbooks
- The current attribute-based configuration approach will be converted to Ansible variables with similar structure
- Service restart and reload notifications will be handled through Ansible handlers rather than Chef notifications