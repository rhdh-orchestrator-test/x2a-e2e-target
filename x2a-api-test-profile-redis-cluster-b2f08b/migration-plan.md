# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 7 custom modules implementing a multi-tier application stack. The migration involves converting profile-based architecture, role-based node classification, and complex Hiera data hierarchies to Ansible playbooks and roles. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with moderate complexity due to PuppetDB queries, custom functions, and multi-level Hiera data structures.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, Bolt tasks, and MOTD management with OS-specific package installation
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom defined types (config_entry, create_dir), Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks, MOTD template management, OS-specific utility packages via Hiera

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL database, systemd service management, and strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, Python virtual environment setup, Gunicorn WSGI server configuration, PostgreSQL database integration, systemd service with security hardening, custom Puppet function for database URL generation

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, SSL termination, stats interface, and optional PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Multi-level Hiera hierarchy (21 levels), SSL/TLS configuration, stats dashboard with authentication, firewall rule management, backend health checks, custom error pages, PuppetDB service discovery

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PGDG APT repository configuration, version-specific package installation, service management with dependency ordering

**profile_redis_cluster**:
- Description: Redis cluster profile using puppet-redis module with PuppetDB node discovery for automatic cluster member detection
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for node discovery, Redis configuration templating, memory management policies, cluster node coordination

**profile**:
- Description: Profile namespace module containing base OS configuration, application stack orchestration, cache management, and load balancer profiles
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Base OS hardening (NTP via chrony, syslog via rsyslog), application stack coordination, cache layer management, load balancer configuration

**role**:
- Description: Role-based node classification module defining server types (app_server, app_stack, haproxy, redis_cluster) with profile composition
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role-based architecture, profile composition patterns, Linux-specific path management, dependency ordering between profiles

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, and apt modules
- `environment.conf`: Module path configuration defining site-modules, modules, and base module paths
- `hiera.yaml`: 4-level hierarchy (per-node, per-OS, per-environment, common) with YAML data backend
- `manifests/site.pp`: Node classification with default role assignment and test Git repository setup
- `data/`: Hiera data directory with environment-specific configurations and OS family overrides
- `Vagrantfile`: Local development environment configuration
- `test/`: Container-based testing infrastructure with Containerfile and test runner

### Target Details

- **Operating System**: Red Hat Enterprise Linux 9 and Ubuntu 24.04 LTS (based on metadata.json operatingsystem_support across modules)
- **Virtual Machine Technology**: Not specified in source configurations
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible community.general collection and custom filters
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template module and file assembly techniques
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw modules
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis configuration tasks
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and ansible.builtin.apt modules

### Security Considerations

- **Hiera encrypted data**: Multiple modules contain sensitive data in Hiera YAML files that need migration to Ansible Vault:
  - Database passwords (profile_app_stack::db_password)
  - Application secret keys (profile_app_stack::secret_key)
  - HAProxy stats passwords (profile_haproxy::stats_password)
  - Redis authentication (profile_redis_cluster::redis_password)
  - SSL certificate paths and configurations
- **Systemd security hardening**: profile_app_stack systemd service template includes extensive security features (NoNewPrivileges, ProtectSystem, PrivateTmp) that need preservation in Ansible service configurations
- **SSH hardening configurations**: Common Hiera data includes SSH security settings that need migration to Ansible ssh configuration modules
- **File permissions and ownership**: Multiple modules manage sensitive file permissions that require careful translation to Ansible file module parameters

### Technical Challenges

- **PuppetDB queries**: profile_redis_cluster uses PuppetDB queries for dynamic node discovery - requires replacement with Ansible inventory plugins or dynamic inventory scripts
- **Custom Puppet functions**: profile_app_stack includes custom Ruby function (app_db_url.rb) for database URL generation - needs conversion to Jinja2 filters or Ansible lookup plugins
- **Multi-level Hiera hierarchy**: 21-level hierarchy in profile_haproxy requires careful mapping to Ansible variable precedence and group_vars/host_vars structure
- **Puppet EPP templates**: Complex systemd service template with parameter validation needs conversion to Jinja2 with equivalent parameter handling
- **Dependency ordering**: Strict dependency chains (Class['A'] -> Class['B'] ~> Class['C']) need translation to Ansible handler notifications and task dependencies
- **Defined types**: base_utils module contains custom defined types that need conversion to Ansible roles or included tasks with parameter passing

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and helper functions used by other modules
2. **profile_postgresql** (moderate complexity) - Database layer with straightforward package/service management
3. **profile** (low complexity) - Base OS configuration profiles with standard package/service patterns
4. **profile_app_stack** (high complexity) - Complex application deployment with custom functions and strict dependencies
5. **profile_haproxy** (high complexity) - Load balancer with multi-level Hiera and optional PuppetDB integration
6. **profile_redis_cluster** (highest complexity) - Requires PuppetDB query replacement and cluster coordination
7. **role** (low complexity) - Role composition layer, depends on all profiles being migrated first

### Assumptions

- Target environments will maintain the same OS support matrix (RHEL 8/9, Ubuntu 22.04/24.04, Debian 11/12) as defined in module metadata
- PuppetDB functionality can be replaced with Ansible inventory plugins or external service discovery mechanisms
- Existing Hiera data structure and values are accurate and will be preserved in Ansible variable files
- SSL certificates referenced in HAProxy configuration are managed externally and paths will remain consistent
- Application deployment patterns (Git repository, Python virtual environments, Gunicorn configuration) will remain unchanged
- PostgreSQL and Redis cluster architectures will maintain current topology and configuration patterns
- Systemd service security hardening requirements will be preserved in Ansible service configurations
- Current firewall management approach can be replaced with equivalent Ansible firewall modules
- Test infrastructure (Vagrant, containers) will be replaced with Ansible-compatible testing frameworks (molecule, ansible-test)