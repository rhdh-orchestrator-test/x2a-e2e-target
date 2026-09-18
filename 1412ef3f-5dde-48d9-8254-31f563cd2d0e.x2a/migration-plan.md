# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a sophisticated Puppet control repository with 8 distinct modules implementing a multi-tier application stack. The migration involves converting role-based profiles, complex Hiera hierarchies, and PuppetDB integrations to Ansible equivalents. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with moderate complexity due to the layered profile/role architecture and cross-module dependencies.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, and MOTD management with OS-specific package installation
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks, platform-specific Facter facts, MOTD template management

**profile_app_stack**:
- Description: Full application stack orchestrator managing Python applications with PostgreSQL database, systemd service management, and strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Custom database URL function, Git repository deployment via vcsrepo, Gunicorn worker configuration, logrotate integration, environment-specific configuration

**profile_haproxy**:
- Description: HAProxy load balancer with SSL termination, multi-backend support, stats interface, and firewall integration
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, SSL/TLS configuration, custom error pages, PuppetDB service discovery, backend health checks

**profile_postgresql**:
- Description: PostgreSQL database server installation with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, version-specific package management, service orchestration

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query integration for cluster member discovery, memory policy configuration, custom Facter facts for Redis role detection

**profile**:
- Description: Thin wrapper profiles providing environment-aware delegation to specific profile modules
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Base OS configuration (NTP, syslog, utilities), environment fact integration, profile composition patterns

**role**:
- Description: Role definitions implementing the roles-and-profiles pattern for node classification
- Path: site-modules/role
- Technology: Puppet
- Key Features: Dependency ordering between profiles, OS-specific execution path configuration, role-based node classification

**puppetdb_query_stub**:
- Description: PuppetDB query function stub providing fallback behavior when PuppetDB is unavailable
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Ruby function implementation, graceful degradation for PuppetDB queries

### Infrastructure Files

- `Puppetfile`: External module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules precedence over Forge modules
- `hiera.yaml`: 4-level hierarchy (node → OS → environment → common) for configuration data
- `data/`: Hierarchical configuration data with environment-specific overrides and OS family variations
- `manifests/site.pp`: Main site manifest for node classification (not present in tree, likely minimal)
- `Vagrantfile`: Development environment configuration for local testing
- `test/`: Containerized testing infrastructure with Docker/Podman support

### Target Details

- **Operating System**: Red Hat Enterprise Linux 9, Ubuntu 22.04/24.04, Debian 11/12 (multi-OS support required based on metadata.json specifications)
- **Virtual Machine Technology**: Not specified in configurations
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general collections
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules and custom configuration templates
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd and ansible.builtin.service modules
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and ansible.builtin.apt modules

### Security Considerations

- **Hardcoded Passwords**: Multiple modules contain hardcoded test passwords in Hiera data (haproxy stats, database, Redis, application secret keys) - migrate to Ansible Vault
- **SSL/TLS Configuration**: HAProxy module manages SSL certificates and cipher suites - ensure proper certificate management in Ansible
- **Database Credentials**: Application stack module handles database connection strings with embedded passwords - implement Ansible Vault integration
- **SSH Hardening**: Base configuration includes SSH security settings - migrate to ansible.posix.sshd_config
- **Service Account Management**: Application stack creates dedicated users and groups - ensure proper privilege separation in Ansible

### Technical Challenges

- **PuppetDB Integration**: Redis cluster module uses PuppetDB queries for node discovery - replace with Ansible inventory groups or dynamic inventory scripts
- **Custom Puppet Functions**: Base utilities module contains custom Ruby functions (ensure_value, normalize_port, app_db_url) - reimplement as Ansible filters or lookup plugins
- **Complex Hiera Hierarchy**: 21-level hierarchy in HAProxy module requires careful mapping to Ansible group_vars and host_vars structure
- **Dependency Ordering**: Strict dependency chains in application stack (python → database → app → service → monitoring) - implement with Ansible handlers and task dependencies
- **Template Complexity**: HAProxy configuration template uses complex ERB logic - convert to Jinja2 with equivalent conditional rendering
- **Facter Integration**: Custom facts for platform info and Redis roles - replace with Ansible custom facts or setup module extensions

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and helper functions needed by other modules
2. **profile_postgresql** (moderate complexity) - Database layer with minimal external dependencies
3. **profile_redis_cluster** (high complexity) - Requires PuppetDB replacement strategy but isolated functionality
4. **profile_haproxy** (high complexity) - Complex configuration but well-defined load balancer role
5. **profile_app_stack** (highest complexity) - Orchestrates multiple components with strict dependency ordering
6. **profile** (low risk) - Thin wrappers, migrate after underlying profiles are complete
7. **role** (low risk) - Node classification layer, migrate last after all profiles are functional
8. **puppetdb_query_stub** (low priority) - Utility module, migrate as needed for PuppetDB replacement

### Assumptions

- The repository follows Puppet's roles-and-profiles pattern consistently, allowing clean separation of concerns during migration
- PuppetDB functionality can be replaced with Ansible inventory management and group-based node discovery
- The 4-level Hiera hierarchy (node/OS/environment/common) maps cleanly to Ansible's group_vars/host_vars structure
- Custom Puppet functions have equivalent implementations available in Ansible or can be rewritten as custom filters
- The target infrastructure supports Ansible's agentless architecture and SSH-based management
- Environment-specific configuration (production/staging) will be managed through Ansible inventory groups rather than Puppet environments
- SSL certificate management currently handled by Puppet can be migrated to Ansible certificate modules or external certificate management systems
- The testing infrastructure (Vagrant/Docker) can be adapted to support Ansible playbook testing with molecule or similar frameworks
- Database and application deployment patterns can be replicated using Ansible's git, template, and service modules without loss of functionality
- Firewall management complexity in the HAProxy profile can be simplified using Ansible's firewall modules while maintaining security posture