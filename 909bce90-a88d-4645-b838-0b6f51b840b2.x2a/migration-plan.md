# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 5 custom site modules implementing a multi-tier application infrastructure. The migration involves converting role-based node classification, Hiera data hierarchies, and profile-based configuration management to Ansible playbooks and roles. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with 2 weeks for planning, 4 weeks for core migration, and 1-2 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Facter facts, Bolt tasks for health checks, ERB templates for MOTD, defined types for configuration management

**profile_app_stack**:
- Description: Full application stack orchestrator managing Python applications with PostgreSQL backend, systemd service management, and monitoring integration
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Strict dependency chain orchestration, custom Puppet function for database URL generation, Git repository deployment via vcsrepo, systemd service templates, log rotation configuration

**profile_haproxy**:
- Description: HAProxy load balancer profile with SSL termination, multi-backend support, statistics interface, and optional PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy for configuration, SSL/TLS configuration, firewall integration, custom error pages, backend health checks, PuppetDB query integration

**profile_postgresql**:
- Description: PostgreSQL database server installation with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PostgreSQL official repository setup, version-specific package management, service lifecycle management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query for cluster node discovery, memory policy configuration, password authentication, custom Facter facts for Redis role detection

**role**:
- Description: Role-based node classification providing composition patterns for different server types
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role composition (app_stack, haproxy, redis_cluster), profile orchestration, Linux-specific exec path management

**profile**:
- Description: Thin wrapper profiles providing abstraction layer between roles and implementation modules
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Environment-aware profile delegation, clean separation between role composition and implementation details

### Infrastructure Files

- `Puppetfile`: External module dependencies from Puppet Forge - requires mapping to Ansible Galaxy roles or custom implementations
- `environment.conf`: Module path configuration - needs translation to Ansible directory structure and ansible.cfg
- `hiera.yaml`: 4-level data hierarchy (node → OS → environment → common) - requires conversion to Ansible group_vars and host_vars structure
- `data/`: Hiera data files with environment-specific and OS-specific configurations - needs restructuring for Ansible inventory
- `manifests/site.pp`: Main site manifest for node classification - requires conversion to Ansible inventory and playbook structure
- `Vagrantfile`: Development environment setup - may need updates for Ansible provisioning
- `test/`: Container-based testing infrastructure - requires adaptation for Ansible testing frameworks

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 based on metadata.json operatingsystem_support declarations
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible built-in modules and community.general collection
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template and assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hiera encrypted data**: Database passwords, Redis authentication, HAProxy stats credentials, and application secret keys are stored in plain text in Hiera YAML files - requires migration to Ansible Vault
- **SSL/TLS certificates**: HAProxy SSL configuration references certificate and key paths - needs secure certificate deployment strategy
- **Service authentication**: Multiple services use hardcoded passwords (test-db-password, test-haproxy-password, test-redis-password) - requires proper secret management
- **SSH hardening**: SSH configuration in Hiera (permit_root_login: false, client_alive_interval) needs translation to Ansible SSH hardening roles
- **Application secrets**: profile_app_stack uses secret_key parameter for application security - requires Ansible Vault integration

### Technical Challenges

- **PuppetDB integration**: profile_haproxy and profile_redis_cluster use PuppetDB queries for service discovery - requires replacement with Ansible dynamic inventory or service discovery mechanisms
- **Custom Puppet functions**: base_utils and profile_app_stack contain custom Ruby functions (ensure_value, normalize_port, app_db_url) - need conversion to Ansible filters or lookup plugins
- **Hiera hierarchy complexity**: 21-level hierarchy in profile_haproxy requires careful mapping to Ansible's group_vars precedence system
- **Dependency orchestration**: profile_app_stack uses strict Puppet dependency chains with notify relationships - needs conversion to Ansible handlers and task dependencies
- **Cross-platform support**: Modules support multiple OS families (RedHat, Debian, Ubuntu) - requires Ansible conditional logic and OS-specific variables
- **Facter custom facts**: Custom Ruby facts for platform info, HAProxy version, and Redis role detection need conversion to Ansible custom facts or setup module extensions

### Migration Order

1. **base_utils** (low risk, foundational): Core utilities and helper functions - establishes patterns for custom facts and cross-platform support
2. **profile_postgresql** (moderate complexity): Database foundation with repository management - required by application stack
3. **profile_redis_cluster** (high complexity): Redis with PuppetDB integration - complex service discovery patterns
4. **profile_app_stack** (high complexity): Application orchestration with strict dependencies - core business logic
5. **profile_haproxy** (highest complexity): Load balancer with advanced Hiera hierarchy and service discovery - most complex configuration management

### Assumptions

- The target Ansible environment will use a similar inventory structure to the current Puppet node classification (roles and profiles pattern)
- PuppetDB functionality can be replaced with Ansible dynamic inventory or external service discovery tools
- The current Hiera data hierarchy can be flattened into Ansible's group_vars and host_vars structure without losing configuration granularity
- Custom Puppet functions can be successfully converted to Ansible filters or lookup plugins without significant logic changes
- The existing test infrastructure in the test/ directory can be adapted for Ansible testing frameworks like Molecule
- SSL certificates and other security artifacts are managed externally and can be integrated with Ansible Vault
- The current Git-based deployment model in profile_app_stack can be maintained using Ansible's git module
- Systemd service management patterns will translate directly to Ansible's systemd module capabilities
- The existing Vagrant development environment can be updated to use Ansible provisioning instead of Puppet