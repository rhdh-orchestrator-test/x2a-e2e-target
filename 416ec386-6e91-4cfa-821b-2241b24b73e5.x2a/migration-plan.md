# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 7 custom modules implementing a complete application stack infrastructure. The migration involves converting Puppet manifests, Hiera data, and ERB templates to Ansible playbooks, roles, and Jinja2 templates. Estimated timeline: 6-8 weeks for a team of 2-3 engineers with moderate Puppet/Ansible experience.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **base_utils**:
    - Description: Base utility module providing common helpers, MOTD management, and utility package installation with Hiera-driven configuration
    - Path: site-modules/base_utils
    - Technology: Puppet
    - Key Features: MOTD template management, utility package arrays, defined types for config entries and directory creation

- **profile**:
    - Description: Profile wrapper module containing thin delegation classes for base OS configuration, application stack, load balancer, and cache services
    - Path: site-modules/profile
    - Technology: Puppet
    - Key Features: Role/profile pattern implementation, base OS hardening (NTP, syslog, SSH), delegation to specialized profile modules

- **profile_app_stack**:
    - Description: Complete Python application deployment with PostgreSQL integration, systemd service management, and database migrations
    - Path: site-modules/profile_app_stack
    - Technology: Puppet
    - Key Features: Git repository cloning, Python virtualenv creation, pip requirements installation, environment file templating, Alembic database migrations, health check scripts

- **profile_haproxy**:
    - Description: HAProxy load balancer with multi-backend support, SSL termination, stats interface, and dynamic backend discovery via PuppetDB queries
    - Path: site-modules/profile_haproxy
    - Technology: Puppet
    - Key Features: Concat-based configuration fragments, firewall rule management, SSL certificate handling, stats authentication, backend health checks

- **profile_postgresql**:
    - Description: PostgreSQL database server installation and configuration with version management and repository setup
    - Path: site-modules/profile_postgresql
    - Technology: Puppet
    - Key Features: PostgreSQL 15 installation, repository configuration, service management, basic database setup

- **profile_redis_cluster**:
    - Description: Redis cluster configuration with PuppetDB-based node discovery and memory management policies
    - Path: site-modules/profile_redis_cluster
    - Technology: Puppet
    - Key Features: PuppetDB queries for cluster member discovery, memory policy configuration, authentication setup

- **role**:
    - Description: Role definitions implementing the role/profile pattern with app_server role orchestrating the complete application stack
    - Path: site-modules/role
    - Technology: Puppet
    - Key Features: Role composition pattern, dependency orchestration between profiles, app_server role combining base, HAProxy, application stack, and Redis cache

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, apt, and inifile modules
- `environment.conf`: Module path configuration defining site-modules as primary modulepath
- `hiera.yaml`: 5-level hierarchy with per-node, OS family, environment, and common data sources
- `manifests/site.pp`: Main site manifest with test Git repository setup and node classification
- `data/common.yaml`: Common Hiera data with application configuration, database credentials, and service parameters
- `data/environment/`: Environment-specific overrides for production and staging with NTP and syslog server configurations
- `Vagrantfile`: Local development environment setup for testing
- `test/`: Container-based testing framework using Podman with systemd init and Puppet apply validation

### Target Details

- **Operating System**: Red Hat Enterprise Linux 9 (primary), with support for Debian 11-12 and Ubuntu 22.04-24.04 based on module metadata
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic with local development via Vagrant

## Migration Approach

### Key Dependencies to Address
- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin modules and community.general collection
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw roles
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or geerlingguy.redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd and ansible.builtin.service modules
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules
- **puppetlabs-inifile (6.1.1)**: Replace with community.general.ini_file module

### Security Considerations
- **Hardcoded credentials in Hiera data**: 
  - Database password: "test-db-password" in profile_app_stack::db_password
  - HAProxy stats password: "test-haproxy-password" in profile_haproxy::stats_password  
  - Redis password: "test-redis-password" in profile_redis_cluster::redis_password
  - Application secret key: "test-secret-key" in profile_app_stack::secret_key
  - Migration approach: Implement Ansible Vault for all credential storage with separate vault files per environment
- **SSL certificate management**: HAProxy module references SSL cert/key paths but SSL is disabled by default - implement proper certificate deployment with Ansible Vault
- **Database connection strings**: Built dynamically in profile_app_stack::app_db_url function - replace with Ansible template generation
- **Environment-based security controls**: ERB template conditionally sets DEBUG and CORS based on environment fact - replicate with Jinja2 templates and group_vars
- **File permissions**: Sensitive files like .env have mode 0600 - ensure Ansible tasks maintain proper permissions
- **Service user isolation**: Application runs as dedicated appuser - maintain user/group isolation in Ansible roles

### Technical Challenges
- **PuppetDB queries for service discovery**: profile_redis_cluster uses PuppetDB to discover cluster members - replace with Ansible inventory groups or dynamic inventory scripts
- **Puppet function dependencies**: profile_app_stack::app_db_url custom function builds database URLs - convert to Jinja2 template or Ansible filter plugin
- **Concat module complexity**: HAProxy configuration uses concat fragments for backend definitions - replace with Jinja2 template loops and include statements
- **Strict dependency chains**: profile_app_stack enforces strict ordering with -> and ~> operators - implement with Ansible handlers and task dependencies
- **ERB template logic**: Complex conditional logic in app.env.erb template - convert to Jinja2 with equivalent conditionals
- **Exec resource idempotency**: Multiple exec resources with unless/creates parameters - replace with appropriate Ansible modules (pip, git, command with creates)
- **Vcsrepo latest revision**: Git repository kept at latest revision - implement with Ansible git module and proper change detection

### Migration Order
1. **base_utils** (low risk, foundational): Simple package installation and file management, no external dependencies
2. **profile_postgresql** (moderate complexity): Database installation with repository setup, required by app stack
3. **profile_redis_cluster** (high complexity): Requires PuppetDB query replacement and cluster coordination logic
4. **profile_app_stack** (highest complexity): Complex application deployment with multiple dependencies, custom functions, and strict ordering
5. **profile_haproxy** (high complexity): Concat-based configuration requiring template restructuring and backend discovery
6. **profile** (low risk): Simple wrapper classes, migrate after component profiles complete
7. **role** (low risk): Role composition, migrate last to orchestrate all components

### Assumptions
- Test credentials in Hiera data are placeholders and production systems use proper secret management
- The test Git repository setup in site.pp is for development only and not required in production
- HAProxy backend discovery via PuppetDB can be replaced with static inventory groups or service discovery integration
- PostgreSQL database creation and user provisioning are handled externally or will be added to the migration scope
- The container-based testing approach can be adapted to use Ansible and molecule for role testing
- Environment-specific configurations in data/environment/ represent the complete set of environment overrides needed
- The role/profile pattern will be maintained in Ansible using a similar group_vars and role composition approach
- SSL certificate deployment is out of scope since SSL is disabled in the current configuration
- Application health checks and monitoring integration beyond the basic health check script are handled separately