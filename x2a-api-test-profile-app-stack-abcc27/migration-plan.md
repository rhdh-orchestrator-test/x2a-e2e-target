# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a sophisticated Puppet control repository implementing a multi-tier application stack with load balancing, caching, and database components. The migration involves 6 distinct Puppet modules plus role/profile architecture, requiring careful coordination of dependencies and configuration management. Estimated timeline: 8-12 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks and rolling restarts, platform-specific Hiera data, MOTD template management

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL backend, systemd service management, and strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment, Python virtual environment setup, database URL generation via custom functions, systemd service templates, log rotation, environment-specific configuration

**profile_haproxy**:
- Description: HAProxy load balancer with SSL termination, multi-backend support, service discovery, and comprehensive monitoring
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, SSL/TLS configuration, backend discovery via PuppetDB queries, firewall integration, stats interface, custom error pages

**profile_postgresql**:
- Description: PostgreSQL database server installation and configuration with version management and repository setup
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: Version-specific package management, repository configuration, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with memory management, password authentication, and cluster node discovery
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB-based node discovery, memory policy configuration, cluster-aware setup

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing and development environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query functionality for non-production environments

**profile (wrapper classes)**:
- Description: Profile wrapper classes implementing the roles and profiles pattern for application, base OS, cache, and load balancer components
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Thin delegation wrappers, environment-aware configuration, role composition

**role**:
- Description: Role classes defining complete node configurations by combining multiple profiles
- Path: site-modules/role
- Technology: Puppet
- Key Features: Multi-component role definitions (app_server, app_stack), dependency ordering

### Infrastructure Files

- `Puppetfile`: External module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, apt, and inifile modules
- `environment.conf`: Module path configuration defining site-modules, modules, and base module paths
- `hiera.yaml`: 4-level hierarchy (per-node, per-OS, per-environment, common) for configuration data
- `manifests/site.pp`: Site-wide configuration with test Git repository setup and default node classification
- `data/`: Hierarchical configuration data with environment-specific overrides and OS-specific settings
- `Vagrantfile`: Development environment provisioning for testing
- `test/`: Container-based testing infrastructure with Containerfile and test runner

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Debian 11/12, Ubuntu 22.04/24.04 (multi-platform support based on metadata.json specifications)
- **Virtual Machine Technology**: Not specified (development uses Vagrant, production platform unclear)
- **Cloud Platform**: Not specified (no cloud-specific configurations detected)

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible community.general collection and custom filters
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template assembly and lineinfile modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules and custom configuration
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd and service modules
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and apt modules

### Security Considerations

- **Hardcoded passwords**: Multiple test passwords found in common.yaml (haproxy, database, redis, secret keys) - migrate to Ansible Vault
- **SSH hardening**: SSH configuration parameters (client_alive_interval, permit_root_login) need migration to ansible.posix.sshd_config
- **SSL/TLS certificates**: HAProxy SSL configuration with certificate and key paths requires secure credential management
- **Database credentials**: PostgreSQL connection strings with embedded passwords need Ansible Vault encryption
- **Service authentication**: Redis password authentication and HAProxy stats credentials require vault management
- **Git repository access**: Application deployment from Git repositories may contain embedded credentials

### Technical Challenges

- **PuppetDB query replacement**: profile_redis_cluster and profile_haproxy use PuppetDB queries for service discovery - requires Ansible dynamic inventory or fact gathering alternatives
- **Custom Puppet functions**: base_utils contains custom functions (ensure_value, normalize_port) and profile_app_stack has app_db_url function - need equivalent Ansible filters or lookup plugins
- **Hiera hierarchy complexity**: 21-level hierarchy in profile_haproxy requires careful variable precedence mapping in Ansible
- **Strict dependency chains**: profile_app_stack enforces strict ordering (python -> database -> app -> service -> monitoring) - requires Ansible handler and dependency management
- **Cross-platform support**: Modules support RHEL, Debian, and Ubuntu with OS-specific configurations - needs Ansible when conditions and OS-specific variable files
- **Bolt task integration**: base_utils includes Bolt tasks for health checks and rolling restarts - requires Ansible playbook equivalents

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and helper functions used by other modules
2. **profile_postgresql** (moderate complexity) - Database foundation required by application stack
3. **profile_redis_cluster** (moderate complexity, PuppetDB dependency) - Caching layer with service discovery challenges
4. **profile_haproxy** (high complexity) - Load balancer with complex Hiera hierarchy and SSL configuration
5. **profile_app_stack** (highest complexity) - Application orchestrator with strict dependencies and custom functions
6. **profile wrapper classes** (low complexity) - Simple delegation wrappers, migrate after underlying profiles
7. **role classes** (low complexity) - Role composition, migrate last after all profiles complete

### Assumptions

- Production environment uses the same OS distributions specified in metadata.json (RHEL 8/9, Debian 11/12, Ubuntu 22.04/24.04)
- Current Puppet infrastructure uses PuppetDB for service discovery and exported resources
- SSL certificates referenced in HAProxy configuration are managed externally or via separate certificate management system
- Test passwords in common.yaml are placeholders and production uses different credential management
- Git repositories referenced in profile_app_stack are accessible from target Ansible control node
- Firewall management approach (currently disabled with "none" provider) will be determined during migration
- Container and Vagrant testing infrastructure will be replaced with Ansible molecule or similar testing framework
- Custom Puppet functions can be replaced with equivalent Ansible filters or lookup plugins without functionality loss
- Service discovery currently handled by PuppetDB queries can be replaced with Ansible dynamic inventory or alternative discovery mechanisms