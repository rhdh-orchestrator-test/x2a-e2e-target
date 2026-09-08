# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a comprehensive Puppet control repository implementing a multi-tier application stack with HAProxy load balancing, Python application deployment, PostgreSQL database, and Redis caching. The migration involves 8 distinct Puppet modules with complex interdependencies, Hiera hierarchical data management, and sophisticated templating. Estimated migration timeline: 6-8 weeks for a team of 2-3 engineers with moderate complexity due to custom functions, strict dependency chains, and multi-environment configuration management.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **base_utils**:
    - Description: Base utility module providing common helpers, defined types, functions, and Bolt tasks with MOTD management and utility package installation
    - Path: site-modules/base_utils
    - Technology: Puppet
    - Key Features: Template-driven MOTD, configurable utility packages, custom defined types (config_entry, create_dir, managed_notify), Bolt tasks and plans

- **profile**:
    - Description: Thin wrapper profiles implementing the roles and profiles pattern with base OS configuration, application stack delegation, load balancer management, and cache service orchestration
    - Path: site-modules/profile
    - Technology: Puppet
    - Key Features: Base OS profile with NTP/syslog management, delegation to specialized profile modules, environment-aware configuration

- **profile_app_stack**:
    - Description: Full application stack profile managing Python application deployment with PostgreSQL integration, systemd service management, and database migrations
    - Path: site-modules/profile_app_stack
    - Technology: Puppet
    - Key Features: Git repository cloning via vcsrepo, Python virtualenv management, pip requirements installation, Alembic database migrations, custom Puppet function for database URL construction, environment file templating

- **profile_haproxy**:
    - Description: HAProxy load balancer profile with multi-backend support, SSL termination, stats interface, and dynamic backend discovery
    - Path: site-modules/profile_haproxy
    - Technology: Puppet
    - Key Features: ERB and EPP template-driven configuration, concat-based backend management, firewall integration, SSL/TLS configuration, stats dashboard with authentication, service discovery capabilities

- **profile_postgresql**:
    - Description: PostgreSQL database server configuration with version management, repository setup, and service orchestration
    - Path: site-modules/profile_postgresql
    - Technology: Puppet
    - Key Features: PostgreSQL 15 installation, repository management, service configuration, Hiera-driven parameter management

- **profile_redis_cluster**:
    - Description: Redis cluster configuration with password authentication, memory management, and systemd integration
    - Path: site-modules/profile_redis_cluster
    - Technology: Puppet
    - Key Features: Redis cluster setup, password-based authentication, memory limit configuration, template-driven redis.conf management

- **puppetdb_query_stub**:
    - Description: PuppetDB query stub library providing custom functions for database queries and service discovery
    - Path: site-modules/puppetdb_query_stub
    - Technology: Puppet
    - Key Features: Custom Ruby functions for PuppetDB integration, service discovery helpers

- **role**:
    - Description: Role definitions implementing the roles and profiles pattern with application server, HAProxy, and Redis cluster role compositions
    - Path: site-modules/role
    - Technology: Puppet
    - Key Features: Role composition (app_server, app_stack, haproxy, redis_cluster), profile orchestration, dependency management

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, apt modules with version pinning
- `environment.conf`: Module path configuration defining site-modules, modules, and base module path hierarchy
- `hiera.yaml`: 5-level Hiera hierarchy with per-node, per-OS family, per-environment, and common data layers
- `manifests/site.pp`: Main site manifest with test Git repository setup and node classification including role::app_server assignment
- `data/common.yaml`: Common Hiera data with NTP, SSH, logging, and module-specific parameters including sensitive data (passwords, secrets)
- `data/environment/production.yaml`: Production environment overrides for NTP servers and syslog configuration
- `data/environment/staging.yaml`: Staging environment overrides for syslog server configuration
- `Vagrantfile`: Local development environment configuration for testing
- `vagrant-provision.sh`: Vagrant provisioning script for development setup
- `test/`: Container-based testing framework with Containerfile and run.sh for validation

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Debian 11/12, Ubuntu 22.04/24.04 (multi-OS support defined in metadata.json files)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general collections for standard library functions
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble for file concatenation
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw for firewall management
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git for Git repository management
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules and custom Redis configuration tasks
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd for service management
- **puppetlabs-inifile (6.1.1)**: Replace with community.general.ini_file for INI file management
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository for package management

### Security Considerations

- **Hiera encrypted data**: Migrate encrypted Hiera data to Ansible Vault for secrets management
- **Hardcoded credentials in common.yaml**: 4 sensitive credentials identified requiring Ansible Vault migration:
  - profile_haproxy::stats_password: "test-haproxy-password"
  - profile_app_stack::db_password: "test-db-password"
  - profile_app_stack::secret_key: "test-secret-key"
  - profile_redis_cluster::redis_password: "test-redis-password"
- **SSL/TLS certificate management**: HAProxy SSL configuration requires certificate deployment strategy in Ansible
- **Environment variable secrets**: Application .env file contains sensitive database URLs and API keys requiring secure templating
- **File permissions**: Sensitive configuration files (e.g., .env with mode 0600) require proper Ansible file module permissions

### Technical Challenges

- **Custom Puppet functions**: profile_app_stack::app_db_url function requires reimplementation as Jinja2 template or custom Ansible filter
- **Strict dependency chains**: Complex dependency relationships (python -> database -> app ~> service -> monitoring) require careful Ansible task ordering and handlers
- **Multi-environment Hiera hierarchy**: 5-level hierarchy (per-node, per-OS, per-environment, common) requires Ansible group_vars and host_vars restructuring
- **ERB/EPP template migration**: HAProxy configuration templates require conversion from ERB to Jinja2 with variable mapping
- **Concat-based configuration**: HAProxy backend configuration using concat fragments requires Ansible template assembly strategy
- **PuppetDB integration**: Custom PuppetDB query functions require replacement with Ansible inventory or dynamic inventory scripts
- **Bolt tasks and plans**: base_utils Bolt tasks require migration to Ansible ad-hoc commands or playbooks
- **Service discovery**: HAProxy dynamic backend discovery requires Ansible service discovery mechanism

### Migration Order

1. **base_utils** (low risk, foundational): Simple utility module with minimal dependencies, provides foundation for other modules
2. **profile_postgresql** (moderate complexity): Database layer required by application stack, manageable scope with clear boundaries
3. **profile_redis_cluster** (moderate complexity): Cache layer with straightforward Redis configuration, limited template complexity
4. **profile** (low complexity): Thin wrapper profiles with simple delegation patterns, minimal logic to migrate
5. **profile_app_stack** (high complexity): Complex application deployment with Git, Python, virtualenv, and database integration
6. **profile_haproxy** (high complexity): Sophisticated load balancer configuration with SSL, stats, and dynamic backends
7. **puppetdb_query_stub** (high complexity): Custom functions requiring significant rework for Ansible equivalents
8. **role** (low complexity): Simple role composition, depends on all profile modules being completed

### Assumptions

- Target environments will maintain the same multi-OS support (RHEL 8/9, Debian 11/12, Ubuntu 22.04/24.04) as defined in module metadata
- Existing Hiera data structure and hierarchy will be preserved through Ansible group_vars/host_vars organization
- HAProxy backend discovery mechanism will be replaced with static configuration or Ansible-based service discovery
- Custom Puppet functions (profile_app_stack::app_db_url) can be adequately replaced with Jinja2 templating
- PuppetDB query functionality will be replaced with Ansible inventory management or eliminated
- Current testing framework using containers will be adapted to Ansible testing with molecule or similar tools
- SSL certificate management strategy exists outside of this migration scope
- Database migration tooling (Alembic) will remain unchanged and be executed through Ansible command modules
- Git repository access and authentication mechanisms will remain consistent across migration
- Systemd service management approach will translate directly to Ansible systemd module usage
- Firewall management will be simplified to use standard Ansible firewall modules without custom rules
- Log rotation and system logging configuration will use standard Ansible approaches rather than custom templates
- The roles and profiles pattern will be maintained in Ansible through proper playbook and role organization
- Environment-specific overrides will be managed through Ansible inventory group variables rather than Hiera hierarchy
- Bolt task functionality will be replaced with equivalent Ansible ad-hoc commands or included in playbooks
- Container-based testing approach will be maintained with Ansible-compatible testing frameworks