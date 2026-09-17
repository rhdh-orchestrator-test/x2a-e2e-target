# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a sophisticated Puppet control repository with 8 modules implementing a multi-tier application stack. The migration involves converting profile-based architecture, complex Hiera hierarchies, and PuppetDB-based service discovery to Ansible equivalents. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with 2-3 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks, platform-specific Hiera data, custom types for validation

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL backend, including git deployment, virtualenv management, systemd service, and database migrations
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Strict dependency chain orchestration, custom Puppet function for database URL generation, Alembic migration support, environment file templating, health check integration

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, SSL termination, stats interface, and PuppetDB-based backend discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, dynamic backend configuration, SSL/TLS with custom ciphers, firewall integration, service discovery via PuppetDB queries

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PGDG repository configuration, version-specific package management, service orchestration

**profile_redis_cluster**:
- Description: Redis cluster profile using puppet-redis module with PuppetDB node discovery for automatic cluster member detection
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query-based node discovery, memory policy configuration, cluster-aware configuration

**puppetdb_query_stub**:
- Description: PuppetDB query function stub providing compatibility layer for PuppetDB queries in testing environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query functionality for development/testing

**profile (namespace module)**:
- Description: Profile namespace containing thin wrapper classes that delegate to dedicated profile modules
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Profile::base::base (OS-level configuration), profile::app::stack (application wrapper), profile::cache::redis, profile::loadbalancer::haproxy

**role (namespace module)**:
- Description: Role definitions implementing the roles-and-profiles pattern for node classification
- Path: site-modules/role
- Technology: Puppet
- Key Features: role::app_server (multi-service node), role::app_stack (application-focused node), role::haproxy, role::redis_cluster

### Infrastructure Files

- `Puppetfile`: External module dependencies including puppetlabs-stdlib, puppetlabs-concat, puppetlabs-firewall, puppetlabs-vcsrepo, puppet-redis, puppetlabs-apt
- `environment.conf`: Module path configuration defining site-modules as primary modulepath
- `hiera.yaml`: 4-level hierarchy (per-node, per-OS, per-environment, common) requiring Ansible equivalent
- `data/common.yaml`: Environment-wide configuration with hardcoded passwords and application settings
- `data/environment/`: Environment-specific overrides for production and staging
- `manifests/site.pp`: Main site manifest for node classification
- `Vagrantfile`: Development environment configuration
- `test/`: Container-based testing infrastructure

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Debian 11/12, Ubuntu 22.04/24.04 (multi-platform support required)
- **Virtual Machine Technology**: Not specified (inferred from Vagrant development setup)
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general collections
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.assemble or template concatenation
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis configuration
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd and ansible.builtin.service

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found in Hiera data (haproxy stats, database, Redis, application secret key) - migrate to Ansible Vault
- **SSL/TLS Configuration**: HAProxy SSL termination with custom cipher suites and certificate management requires careful migration
- **Service Account Management**: Application user/group creation and permission management needs equivalent Ansible user module configuration
- **Database Credentials**: PostgreSQL connection strings with embedded passwords need Ansible Vault integration
- **Environment Files**: Application .env files contain sensitive configuration requiring secure templating

### Technical Challenges

- **PuppetDB Service Discovery**: profile_redis_cluster uses PuppetDB queries for automatic cluster member detection - requires replacement with Ansible dynamic inventory or service discovery mechanism
- **Complex Hiera Hierarchy**: 21-level hierarchy in HAProxy module needs restructuring for Ansible group_vars/host_vars pattern
- **Custom Puppet Functions**: profile_app_stack::app_db_url function needs conversion to Ansible Jinja2 filter or custom module
- **Strict Dependency Orchestration**: profile_app_stack enforces strict class dependency chains that need careful Ansible handler and task ordering
- **Cross-Platform Support**: Modules support multiple OS families requiring Ansible when/ansible_os_family conditionals
- **Template Complexity**: ERB templates with complex logic need conversion to Jinja2 with equivalent functionality

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and platform detection
2. **profile_postgresql** (moderate complexity) - Database foundation for application stack
3. **profile_redis_cluster** (high complexity) - Service discovery challenges but isolated
4. **profile_haproxy** (high complexity) - Complex configuration but well-contained
5. **profile_app_stack** (highest complexity) - Complex orchestration with multiple dependencies
6. **profile namespace and role modules** (low complexity) - Simple wrappers, migrate after components

### Assumptions

- PuppetDB service discovery can be replaced with Ansible dynamic inventory or static configuration
- Current Hiera hierarchy complexity is necessary and should be preserved in Ansible group_vars structure
- All hardcoded passwords in Hiera data are acceptable for migration to Ansible Vault
- Git repository access patterns (file:// URLs in test data) will be updated for production deployment
- Systemd service management approach is compatible across target operating systems
- Python virtualenv management patterns are consistent with Ansible pip module capabilities
- Database migration tooling (Alembic) integration can be replicated in Ansible
- SSL certificate management processes are compatible with Ansible certificate modules
- Firewall management requirements can be met with standard Ansible firewall modules
- Container-based testing approach can be adapted for Ansible playbook testing