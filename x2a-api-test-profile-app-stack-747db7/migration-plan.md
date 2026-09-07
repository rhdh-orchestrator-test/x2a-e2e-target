# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 7 custom modules implementing a multi-tier application stack architecture. The migration involves converting Puppet profiles and roles to Ansible roles, with particular attention to the complex Hiera hierarchy and PuppetDB-based service discovery. Estimated timeline: 8-12 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation across all nodes
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks, platform-specific facts, MOTD templating

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL database, systemd service management, and strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment, Python virtual environment setup, database URL generation via custom functions, Gunicorn configuration, log rotation, environment file templating

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, SSL termination, stats interface, and optional PuppetDB-based backend discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, dynamic backend configuration, SSL certificate management, firewall integration, custom error pages, stats authentication

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, package version control, service management

**profile_redis_cluster**:
- Description: Redis cluster profile using puppet-redis module with PuppetDB node discovery for automatic cluster member detection
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for node discovery, memory policy configuration, cluster-aware setup

**profile**:
- Description: Thin wrapper profiles that delegate to specific profile modules, providing abstraction layer for role composition
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Profile composition patterns, environment-aware configuration, delegation to specialized modules

**role**:
- Description: Role definitions that compose profiles into complete node configurations following the roles-and-profiles pattern
- Path: site-modules/role
- Technology: Puppet
- Key Features: Node classification, profile orchestration, Linux-specific path configuration

### Infrastructure Files

- `Puppetfile`: Main dependency manifest listing Puppet Forge modules (stdlib, concat, firewall, vcsrepo, redis, systemd, apt)
- `environment.conf`: Module path configuration defining site-modules precedence over Forge modules
- `hiera.yaml`: 4-level hierarchy configuration (per-node, per-OS, per-environment, common)
- `manifests/site.pp`: Site manifest with test Git repository setup and default node classification
- `data/common.yaml`: Global Hiera data with application and service configuration defaults
- `data/environment/`: Environment-specific overrides for production and staging
- `Vagrantfile`: Local development environment configuration
- `test/`: Container-based testing infrastructure

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 based on metadata.json specifications across modules
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible community.general collection and custom filters
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template assembly or blockinfile module
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and apt modules

### Security Considerations

- **Credential Management**: Multiple hardcoded passwords identified in Hiera data:
  - HAProxy stats password: "test-haproxy-password"
  - Database password: "test-db-password" 
  - Redis password: "test-redis-password"
  - Application secret key: "test-secret-key"
  - Migration requires implementing Ansible Vault for all credential storage
- **SSL Certificate Handling**: HAProxy module references SSL certificate paths that need secure distribution mechanism
- **Service Authentication**: HAProxy stats interface uses basic authentication requiring secure credential management
- **Database Security**: PostgreSQL user credentials and connection strings need vault encryption
- **File Permissions**: Templates and configuration files use specific ownership and permissions that must be preserved

### Technical Challenges

- **PuppetDB Service Discovery**: profile_redis_cluster uses PuppetDB queries for automatic node discovery - requires replacement with Ansible dynamic inventory or service discovery mechanism
- **Complex Hiera Hierarchy**: 21-level hierarchy in HAProxy module needs restructuring for Ansible group_vars/host_vars pattern
- **Custom Puppet Functions**: base_utils module contains custom functions (ensure_value, normalize_port, app_db_url) requiring conversion to Ansible filters or lookup plugins
- **Strict Dependency Chains**: profile_app_stack enforces strict ordering (python -> database -> app -> service -> monitoring) requiring careful Ansible handler and dependency management
- **Template Complexity**: HAProxy configuration uses complex ERB templating with conditional SSL blocks and dynamic backend iteration
- **Cross-Module Dependencies**: Roles compose multiple profiles with specific ordering requirements that need preservation in Ansible playbooks

### Migration Order

1. **base_utils** (low risk, foundational): Utility functions, MOTD, package management - establishes common patterns
2. **profile_postgresql** (moderate complexity): Database setup with repository management - enables application stack
3. **profile_app_stack** (high complexity): Core application deployment with all dependencies and strict ordering
4. **profile_haproxy** (high complexity): Load balancer with complex templating and backend discovery
5. **profile_redis_cluster** (highest complexity): Requires PuppetDB replacement and cluster coordination
6. **profile and role modules** (integration phase): Composition layer requiring all components to be complete

### Assumptions

- PuppetDB service discovery in Redis cluster can be replaced with static inventory or external service discovery
- SSL certificates referenced in HAProxy configuration are available through secure distribution mechanism
- Test Git repository setup in site.pp is development-only and not required in production Ansible implementation
- Hiera hierarchy complexity can be simplified using Ansible's native variable precedence without losing functionality
- Custom Puppet functions can be adequately replaced with Jinja2 filters and Ansible lookup plugins
- Bolt tasks and plans in base_utils module are not critical for initial migration and can be addressed in later phases
- Container-based testing infrastructure can be adapted to use Ansible testing frameworks like Molecule
- Environment-specific configurations in data/environment/ directories map cleanly to Ansible group_vars structure