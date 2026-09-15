# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 5 custom site modules implementing a multi-tier application stack architecture. The migration involves converting Puppet profiles and roles to Ansible roles, with moderate complexity due to Hiera data hierarchies, PuppetDB queries, and cross-module dependencies. Estimated timeline: 6-8 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks, platform-specific Hiera data, MOTD template management

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL backend, systemd service management, and strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment, database URL construction via custom functions, environment-specific configuration, Gunicorn/Uvicorn worker management, log rotation

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, SSL termination, stats interface, and optional service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, PuppetDB-based backend discovery, firewall integration, SSL/TLS configuration, custom error pages

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, version-specific package installation, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB node discovery, memory management, and cluster-aware configuration
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for node discovery, memory policy configuration, cluster topology management

**role**:
- Description: Role composition module defining server types (app_server, app_stack, haproxy, redis_cluster) with profile orchestration
- Path: site-modules/role
- Technology: Puppet
- Key Features: Profile composition, dependency ordering, OS-specific exec path management

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing environments without PuppetDB connectivity
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query responses for development/testing

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules precedence over Forge modules
- `hiera.yaml`: 4-level hierarchy (node → OS family → environment → common) for configuration data
- `data/`: Hierarchical configuration data with environment-specific overrides and OS-specific settings
- `manifests/site.pp`: Node classification and test application repository setup
- `Vagrantfile`: Development environment provisioning for testing
- `test/`: Container-based testing infrastructure with Containerfile and test runner

### Target Details

- **Operating System**: Red Hat Enterprise Linux 9 and Ubuntu 24.04 LTS (based on metadata.json operatingsystem_support)
- **Virtual Machine Technology**: Not specified in configuration files
- **Cloud Platform**: Not specified - appears to be cloud-agnostic infrastructure

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin collection and community.general modules
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw modules
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hardcoded credentials in Hiera data**: Database passwords, Redis passwords, HAProxy stats passwords, and application secret keys are stored in plain text in YAML files
  - profile_app_stack: db_password, secret_key (2 credentials per module)
  - profile_haproxy: stats_password (1 credential per module)
  - profile_redis_cluster: redis_password (1 credential per module)
- **SSL/TLS certificate management**: HAProxy module references SSL certificate and key paths that need secure distribution
- **SSH hardening configurations**: SSH client settings and root login restrictions defined in Hiera
- **Service account management**: Application user/group creation and permission management in app stack
- **Vault/secrets management**: Migrate to Ansible Vault for encrypted variable storage and implement proper secret rotation

### Technical Challenges

- **PuppetDB query replacement**: profile_redis_cluster and profile_haproxy use PuppetDB queries for service discovery - replace with Ansible inventory groups or dynamic inventory scripts
- **Custom Puppet functions**: base_utils module contains custom functions (ensure_value, normalize_port) and profile_app_stack has app_db_url function - reimplement as Jinja2 filters or custom Ansible modules
- **Hiera hierarchy complexity**: 4-level hierarchy with node-specific, OS-specific, and environment-specific data requires careful Ansible variable precedence planning
- **Strict dependency chains**: profile_app_stack enforces strict ordering (python → database → app → service → monitoring) - implement with Ansible handlers and task dependencies
- **Template variable scoping**: ERB templates access instance variables (@variable) - convert to Jinja2 with proper variable passing
- **Bolt task integration**: base_utils includes Bolt tasks for health checks and rolling restarts - replace with Ansible ad-hoc commands or playbooks

### Migration Order

1. **base_utils** (low risk, foundational): Utility functions and MOTD management - establishes patterns for other modules
2. **profile_postgresql** (moderate complexity): Database installation with repository management - required by app stack
3. **profile_app_stack** (high complexity): Core application deployment with multiple dependencies and custom functions
4. **profile_haproxy** (high complexity): Load balancer with service discovery and SSL configuration
5. **profile_redis_cluster** (high complexity): Cluster configuration with PuppetDB dependencies
6. **role** (low complexity): Role composition after all profiles are migrated

### Assumptions

- **PuppetDB replacement strategy**: Assumes Ansible dynamic inventory or static inventory groups can replace PuppetDB node queries for service discovery
- **Custom function migration**: Assumes custom Puppet functions can be adequately replaced with Jinja2 templates and filters without loss of functionality
- **Hiera data migration**: Assumes current Hiera hierarchy can be flattened into Ansible group_vars and host_vars structure without breaking environment isolation
- **Service discovery mechanism**: Assumes HAProxy backend discovery can transition from PuppetDB queries to Ansible inventory-based discovery
- **Testing environment**: Assumes Vagrant-based testing can be replaced with Molecule or similar Ansible testing framework
- **Git repository access**: Assumes application deployment repositories remain accessible with same authentication mechanisms
- **Certificate management**: Assumes SSL certificates referenced in HAProxy configuration have established distribution mechanisms that can be adapted to Ansible
- **Database connectivity**: Assumes PostgreSQL connection parameters and credentials can be migrated without service interruption
- **Redis cluster topology**: Assumes current Redis cluster node relationships can be maintained through Ansible inventory structure