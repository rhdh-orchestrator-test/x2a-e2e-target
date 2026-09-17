# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a sophisticated Puppet control repository implementing a multi-tier application stack with load balancing, database services, and caching. The migration involves 8 distinct modules with complex interdependencies, Hiera-based configuration management, and PuppetDB integration. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with 2-3 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with custom Puppet functions and Bolt tasks
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom defined types (config_entry, create_dir), Puppet functions (ensure_value, normalize_port), Facter facts, Bolt tasks for health checks and rolling restarts

**profile_app_stack**:
- Description: Full application stack orchestrator managing Python applications with PostgreSQL database, systemd service management, and strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, systemd service templates, log rotation, environment file management, security hardening

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, SSL termination, statistics interface, and optional PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend configuration, SSL/TLS with custom ciphers, statistics dashboard, firewall integration, custom error pages, service discovery

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PGDG repository setup, version-specific package installation, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB node discovery, memory management, and cluster-aware configuration
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster member discovery, memory policy configuration, password authentication

**puppetdb_query_stub**:
- Description: PuppetDB query function stub providing compatibility layer for PuppetDB queries in testing environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Custom Puppet function for PuppetDB integration

**profile**:
- Description: Thin wrapper profiles providing abstraction layer between roles and implementation modules
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Base OS configuration (NTP, syslog, utilities), delegation to specialized profile modules

**role**:
- Description: Role definitions composing multiple profiles into complete node configurations for application servers and load balancers
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role-based node classification, profile composition, dependency ordering

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules precedence over Forge modules
- `hiera.yaml`: 4-level hierarchy (node → OS → environment → common) for configuration data
- `manifests/site.pp`: Node classification and test application repository setup
- `data/common.yaml`: Environment-wide configuration defaults including credentials and application settings
- `data/environment/*.yaml`: Environment-specific overrides for production and staging
- `Vagrantfile`: Local development environment configuration
- `test/`: Container-based testing infrastructure

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 (multi-OS support required based on metadata.json specifications)
- **Virtual Machine Technology**: Not specified (inferred from Vagrant configuration suggesting VirtualBox/VMware compatibility)
- **Cloud Platform**: Not specified (infrastructure-agnostic design)

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general collections
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules and custom configuration
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd and ansible.builtin.template
- **puppetlabs-inifile (6.1.1)**: Replace with community.general.ini_file module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and ansible.builtin.apt modules

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found in data/common.yaml including HAProxy stats password, database credentials, Redis authentication, and application secret keys
- **SSL/TLS Configuration**: HAProxy SSL termination with custom cipher suites and certificate management requiring secure certificate deployment
- **Systemd Security**: Application service includes security hardening (NoNewPrivileges, ProtectSystem, PrivateTmp) that must be preserved
- **Database Security**: PostgreSQL authentication and connection security configurations
- **Vault/secrets management**: 
  - HAProxy: stats_password in Hiera data
  - Application: db_password, secret_key in configuration
  - Redis: redis_password for cluster authentication
  - SSH: hardening configurations in base profile
  - Credentials are currently stored in plaintext YAML files across 5+ modules

### Technical Challenges

- **PuppetDB Integration**: profile_redis_cluster uses PuppetDB queries for dynamic cluster member discovery - requires replacement with Ansible inventory or service discovery mechanism
- **Custom Puppet Functions**: base_utils module contains custom functions (ensure_value, normalize_port, app_db_url) requiring reimplementation in Jinja2 or Ansible filters
- **Complex Dependency Chains**: profile_app_stack enforces strict ordering (python → database → app → service → monitoring) requiring careful Ansible handler and dependency management
- **Hiera Hierarchy**: 4-level configuration hierarchy with OS-specific, environment-specific, and node-specific data requires Ansible group_vars and host_vars restructuring
- **Template Complexity**: HAProxy configuration template with dynamic backend generation and SSL conditional logic requires advanced Jinja2 templating
- **Cross-Module Dependencies**: Roles compose multiple profiles with complex inter-module relationships requiring careful Ansible role design

### Migration Order

1. **base_utils** (low risk, foundational): Core utilities and helper functions used by all other modules
2. **profile_postgresql** (moderate complexity): Database foundation required by application stack
3. **profile** (low complexity): Thin wrapper profiles with minimal logic
4. **profile_app_stack** (high complexity): Complex application deployment with multiple dependencies
5. **profile_haproxy** (high complexity): Load balancer with dynamic configuration and SSL
6. **profile_redis_cluster** (highest complexity): PuppetDB integration and cluster discovery
7. **role** (moderate complexity): Role composition after all profiles are migrated
8. **puppetdb_query_stub** (specialized): Testing infrastructure component

### Assumptions

- PuppetDB service discovery in Redis cluster module will need replacement with static inventory or external service discovery
- Current Hiera data structure can be mapped to Ansible group_vars/host_vars without data loss
- SSL certificates referenced in HAProxy configuration are available through external certificate management
- Git repository access for application deployment (vcsrepo) has appropriate authentication configured
- PostgreSQL PGDG repository access and package availability remains consistent across target environments
- Systemd service management capabilities are available on all target operating systems
- Firewall management approach (iptables vs firewalld vs ufw) needs clarification based on target OS preferences
- Testing infrastructure (Vagrant, containers) will be replaced with Ansible-compatible alternatives
- Custom Facter facts (platform_info, haproxy_version, redis_role) can be replaced with Ansible facts or custom fact gathering
- Bolt task functionality (health_check.pp, rolling_restart.pp) will be reimplemented as Ansible playbooks or roles