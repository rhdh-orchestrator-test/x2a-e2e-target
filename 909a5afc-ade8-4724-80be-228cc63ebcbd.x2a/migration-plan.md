# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a Python FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis 6379, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis authentication (requirepass), custom log directory creation, configuration file manipulation via ruby_block, memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database/user provisioning, systemd service management, environment file configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening, and firewall configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL sites (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo node configuration with run_list and attribute overrides for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning - will need Ansible equivalent for testing
- `vagrant-provision.sh`: Shell provisioning script - may contain additional setup steps to migrate

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on metadata.rb supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: SSL certificates referenced in nginx configuration need secure deployment mechanism
- **SSH Hardening**: Root login disable and password authentication disable configurations need careful migration
- **Firewall Rules**: UFW firewall configuration with specific port allowances (22, 80, 443)
- **Fail2ban Configuration**: Intrusion prevention system configuration via templates
- **Sysctl Security**: Kernel parameter tuning for security hardening

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses ruby_block to manipulate Redis configuration files - needs conversion to Ansible lineinfile or template modules
- **Multi-Recipe Dependencies**: nginx-multisite cookbook has complex recipe interdependencies that need careful ordering in Ansible
- **Service Orchestration**: FastAPI application depends on PostgreSQL being configured first - requires proper task ordering and handlers
- **Template Migration**: ERB templates (.erb) need conversion to Jinja2 (.j2) format
- **Attribute Override Complexity**: solo.json overrides default attributes - needs translation to Ansible variable precedence

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached have minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server foundation needed for application serving
3. **fastapi-tutorial** (high complexity) - Depends on database setup and has the most complex service configuration

### Assumptions

- SSL certificates are manually managed or obtained externally (no automated certificate generation visible in current configuration)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible during migration
- Current Chef Solo deployment model will be replaced with Ansible playbook execution
- Database credentials and Redis passwords will be migrated to Ansible Vault for security
- The three nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) are the complete set of required virtual hosts
- UFW firewall rules are sufficient and no additional iptables configuration is needed
- The ruby_block configuration fixes in the Redis cookbook are still necessary and not resolved by newer Redis versions
- Vagrant development environment will be replaced with equivalent Ansible testing setup
- No Chef encrypted data bags or Chef Vault usage detected - all secrets appear to be in plain text attributes