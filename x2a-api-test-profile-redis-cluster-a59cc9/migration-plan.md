# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a sophisticated Puppet control repository with 8 modules implementing a complete application stack infrastructure. The migration involves converting role-based profiles, complex Hiera hierarchies, and PuppetDB-dependent service discovery to Ansible equivalents. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with 2-3 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks, platform-specific Hiera data, MOTD template management

**profile_app_stack**:
- Description: Full application stack orchestrator managing Python application deployment with PostgreSQL database, systemd service, and monitoring integration
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository cloning via vcsrepo, Python virtualenv management, database migrations with Alembic, systemd service templates, custom database URL function

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, SSL termination, stats interface, and PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend configuration, SSL/TLS with custom ciphers, firewall integration, 21-level Hiera hierarchy, stats authentication

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, version-specific package installation, service management

**profile_redis_cluster**:
- Description: Redis cluster profile using PuppetDB node discovery for automatic cluster member detection and configuration
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query integration, cluster node discovery, memory policy configuration, password authentication

**profile**:
- Description: Profile wrapper classes providing thin interfaces to specific profile modules (base OS, cache, loadbalancer, app stack)
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Role composition patterns, environment-aware configuration, base OS hardening (NTP, syslog, SSH)

**role**:
- Description: Role definitions combining multiple profiles into complete node configurations (app_server, app_stack, haproxy, redis_cluster)
- Path: site-modules/role
- Technology: Puppet
- Key Features: Profile orchestration, dependency management, Linux-specific path configuration

**puppetdb_query_stub**:
- Description: PuppetDB query function stub providing compatibility layer for PuppetDB queries in testing environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query responses, testing infrastructure support

### Infrastructure Files

- `Puppetfile`: External module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, apt modules
- `environment.conf`: Module path configuration defining site-modules precedence over Forge modules
- `hiera.yaml`: 4-level hierarchy (per-node, per-OS, per-environment, common) with YAML backend
- `manifests/site.pp`: Main site manifest for node classification and global configuration
- `data/`: Hiera data directory with environment-specific and common configuration values
- `Vagrantfile`: Local development environment configuration for testing
- `test/`: Container-based testing infrastructure with Containerfile and test runner

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 (multi-platform support required)
- **Virtual Machine Technology**: Not specified (inferred from Vagrant development setup)
- **Cloud Platform**: Not specified (infrastructure-agnostic deployment)

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin collection and community.general modules
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw modules
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules and custom configuration templates
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd and ansible.builtin.template modules
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and ansible.builtin.apt modules

### Security Considerations

- **Hardcoded Credentials**: Multiple modules contain test passwords in Hiera data (haproxy stats, database, Redis) that need Ansible Vault encryption
- **SSL/TLS Configuration**: HAProxy module manages SSL certificates and custom cipher suites requiring secure certificate deployment via Ansible Vault
- **Database Credentials**: Application stack module uses database passwords and secret keys that need vault encryption
- **SSH Hardening**: Base profile implements SSH security settings (root login disabled, client alive intervals) requiring Ansible SSH module configuration
- **Service Authentication**: Redis cluster uses password authentication requiring secure credential distribution

### Technical Challenges

- **PuppetDB Service Discovery**: Redis cluster module uses PuppetDB queries for automatic node discovery - requires replacement with Ansible inventory groups or dynamic inventory scripts
- **Complex Hiera Hierarchy**: 21-level hierarchy in HAProxy module needs restructuring into Ansible group_vars and host_vars with precedence mapping
- **Custom Puppet Functions**: Base utils module contains custom functions (ensure_value, normalize_port) requiring conversion to Ansible filters or custom modules
- **Strict Dependency Chains**: Application stack enforces strict ordering (python -> database -> app -> service -> monitoring) requiring Ansible handler and dependency management
- **Template Complexity**: HAProxy configuration template uses complex ERB logic requiring Jinja2 conversion with conditional blocks
- **Cross-Platform Support**: Modules support multiple OS families (RedHat, Debian, Ubuntu) requiring Ansible when/vars conditional logic

### Migration Order

1. **base_utils** (low risk, foundational): Core utilities and helper functions needed by other modules
2. **profile_postgresql** (moderate complexity): Database foundation required by application stack
3. **profile_redis_cluster** (high complexity): Requires PuppetDB replacement strategy before migration
4. **profile_haproxy** (high complexity): Complex templating and multi-level Hiera hierarchy
5. **profile_app_stack** (highest complexity): Depends on PostgreSQL, complex deployment pipeline with git/virtualenv/migrations
6. **profile, role** (low complexity): Wrapper classes for orchestration, migrate after component profiles
7. **puppetdb_query_stub** (testing only): Migrate last as testing infrastructure

### Assumptions

- **PuppetDB Replacement**: Assumes Ansible dynamic inventory or static inventory groups can replace PuppetDB node queries for service discovery
- **Hiera Data Migration**: Assumes current Hiera YAML structure can be mapped to Ansible group_vars/host_vars without data loss
- **Custom Function Compatibility**: Assumes custom Puppet functions can be replaced with equivalent Ansible filters or custom modules
- **Service Dependencies**: Assumes systemd service dependencies can be managed through Ansible handlers and task ordering
- **Certificate Management**: Assumes SSL certificate deployment process exists outside of Puppet (not defined in reviewed modules)
- **Database Schema**: Assumes application database schema and migration process (Alembic) can be managed through Ansible command/shell modules
- **Testing Infrastructure**: Assumes container-based testing approach can be adapted to Ansible with molecule or similar frameworks
- **Git Repository Access**: Assumes application git repositories remain accessible with same authentication mechanisms for Ansible git module
- **Python Environment**: Assumes Python virtualenv management can be handled through Ansible pip and virtualenv modules with equivalent functionality