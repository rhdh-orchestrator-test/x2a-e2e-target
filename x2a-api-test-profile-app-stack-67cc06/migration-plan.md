# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 6 custom modules implementing a multi-tier application stack architecture. The migration involves converting role-based profiles, Hiera data hierarchies, and PuppetDB queries to Ansible equivalents. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with moderate complexity due to the sophisticated Hiera hierarchy and service discovery patterns.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Facter facts, Bolt tasks, ERB templates, OS-specific Hiera data

**profile_app_stack**:
- Description: Full application stack orchestrator with Python application deployment, PostgreSQL integration, systemd service management, and monitoring
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, strict dependency chains, environment-specific configuration, log rotation

**profile_haproxy**:
- Description: HAProxy load balancer profile with SSL termination, multi-backend support, service discovery, and comprehensive firewall management
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend discovery via PuppetDB queries, SSL/TLS configuration, statistics interface, custom error pages, 21-level Hiera hierarchy

**profile_postgresql**:
- Description: PostgreSQL database server installation and configuration with version management and repository setup
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: Version-specific package management, repository configuration, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with memory management, authentication, and cluster node discovery via PuppetDB
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB-based node discovery, memory policy configuration, cluster-aware setup

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing and development environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query functionality for non-production environments

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, apt, and inifile modules
- `hiera.yaml`: 4-level hierarchy (node-specific, OS family, environment, common) requiring Ansible equivalent data structure
- `environment.conf`: Puppet environment configuration needing conversion to Ansible directory structure
- `manifests/site.pp`: Main site manifest requiring conversion to Ansible inventory and playbook structure
- `data/`: Hiera data files with environment-specific and OS-specific overrides requiring Ansible group_vars/host_vars migration
- `Vagrantfile`: Development environment configuration that can be adapted for Ansible testing
- `test/`: Container-based testing framework requiring adaptation to ansible-test or molecule

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Debian 11/12, Ubuntu 22.04/24.04 (multi-platform support based on metadata.json specifications)
- **Virtual Machine Technology**: Not specified (inferred from Vagrant configuration suggesting VirtualBox/VMware compatibility)
- **Cloud Platform**: Not specified (no cloud-specific configurations detected)

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible built-in modules and community.general collection
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template and assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and apt_repository modules

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found in Hiera data (haproxy stats, database, Redis, application secret key) requiring migration to Ansible Vault
- **SSL/TLS Configuration**: HAProxy SSL certificate and key paths need secure handling via Ansible Vault or external certificate management
- **SSH Hardening**: SSH configuration parameters in Hiera requiring migration to Ansible ssh hardening roles
- **Database Credentials**: PostgreSQL and application database credentials stored in Hiera requiring Ansible Vault encryption
- **Service Discovery**: PuppetDB queries for dynamic configuration need replacement with Ansible inventory plugins or service discovery mechanisms

### Technical Challenges

- **PuppetDB Query Migration**: profile_haproxy and profile_redis_cluster use PuppetDB queries for dynamic backend/node discovery - requires Ansible dynamic inventory or service discovery integration
- **Hiera Hierarchy Complexity**: 4-level hierarchy with node, OS, environment, and common data requires careful mapping to Ansible group_vars/host_vars structure
- **Custom Puppet Functions**: base_utils module contains custom functions (ensure_value, normalize_port, app_db_url) requiring conversion to Ansible filters or lookup plugins
- **Strict Dependency Chains**: profile_app_stack uses Puppet's contain and dependency arrows requiring careful Ansible task ordering and handlers
- **Cross-Platform Support**: Modules support RHEL, Debian, and Ubuntu requiring Ansible conditional logic and OS-specific variables
- **Facter Custom Facts**: Custom facts for platform_info, haproxy_version, and redis_role need conversion to Ansible custom facts or setup module extensions

### Migration Order

1. **base_utils** (low risk, foundational): Core utilities and helper functions used by other modules
2. **profile_postgresql** (moderate complexity): Database foundation required by application stack
3. **profile_app_stack** (high complexity): Application deployment with database integration and service management
4. **profile_redis_cluster** (moderate complexity): Caching layer with cluster discovery challenges
5. **profile_haproxy** (high complexity): Load balancer with dynamic backend discovery and SSL configuration
6. **puppetdb_query_stub** (low risk): Testing utility for development environments

### Assumptions

- PuppetDB service discovery patterns can be replaced with Ansible dynamic inventory or external service discovery tools
- Current Hiera encryption (if any) uses eyaml or similar, requiring migration strategy to Ansible Vault
- Git repositories referenced in vcsrepo resources are accessible from Ansible control node
- SSL certificates referenced in HAProxy configuration are available for Ansible deployment
- Custom Facter facts can be replaced with Ansible setup module extensions or custom fact gathering
- Bolt tasks and plans in base_utils module are not critical for initial migration (can be addressed in later phases)
- Multi-environment support (production/staging) maps cleanly to Ansible inventory groups
- Service restart and notification patterns can be handled via Ansible handlers and task dependencies