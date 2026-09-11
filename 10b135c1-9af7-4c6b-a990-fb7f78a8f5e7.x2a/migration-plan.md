# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 6 custom modules implementing a multi-tier web application stack. The migration involves converting Puppet profiles and roles to Ansible playbooks and roles, with moderate complexity due to Hiera data hierarchies, PuppetDB queries, and template-driven configurations. Estimated timeline: 6-8 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Facter facts, Bolt tasks, ERB templates for MOTD, OS-specific Hiera data

**profile_app_stack**:
- Description: Full application stack orchestrator for Python web applications with PostgreSQL backend, systemd service management, and strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, EPP/ERB templates for systemd service and environment files, logrotate configuration, monitoring integration

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, SSL termination, stats interface, and firewall integration
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Complex ERB template for haproxy.cfg, backend discovery via PuppetDB queries, SSL certificate management, custom error pages, 21-level Hiera hierarchy

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, package version management, service orchestration

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster member discovery, ERB template for redis.conf, custom Facter facts for Redis role detection

**role**:
- Description: Role composition module defining server types (app_server, app_stack, haproxy, redis_cluster) that combine base and profile classes
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role-based node classification, dependency ordering between profiles

### Infrastructure Files

- `Puppetfile`: External module dependencies from Puppet Forge - requires mapping to Ansible Galaxy/Collections
- `environment.conf`: Module path configuration - translate to ansible.cfg and collection requirements
- `hiera.yaml`: 4-level data hierarchy (nodes, OS family, environment, common) - migrate to Ansible group_vars/host_vars structure
- `data/common.yaml`: Global configuration data with hardcoded passwords - requires Ansible Vault migration
- `manifests/site.pp`: Node classification and test Git repository setup - convert to Ansible inventory and playbooks
- `Vagrantfile`: Development environment setup - update for Ansible provisioning

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 (multi-platform support based on metadata.json specifications)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin collection and community.general modules
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found in data/common.yaml requiring Ansible Vault encryption:
  - HAProxy stats password: "test-haproxy-password"
  - Database password: "test-db-password" 
  - Redis password: "test-redis-password"
  - Application secret key: "test-secret-key"
- **SSL Certificate Management**: HAProxy SSL configuration references certificate paths that need secure deployment via Ansible Vault
- **SSH Hardening**: Existing SSH security configurations (permit_root_login: false, client_alive_interval) need preservation in Ansible
- **Service Account Security**: Application user/group management requires proper privilege separation in Ansible playbooks

### Technical Challenges

- **PuppetDB Query Migration**: profile_redis_cluster uses PuppetDB queries for node discovery - replace with Ansible inventory groups or dynamic inventory scripts
- **Custom Puppet Functions**: profile_app_stack::app_db_url function needs conversion to Jinja2 template or Ansible filter plugin
- **Complex Hiera Hierarchy**: 21-level hierarchy in profile_haproxy requires careful mapping to Ansible's group_vars/host_vars precedence
- **Template Complexity**: HAProxy ERB template with conditional SSL blocks needs conversion to Jinja2 with equivalent logic
- **Dependency Ordering**: Strict class containment and dependency chains (profile_app_stack) require careful Ansible handler and task ordering
- **Cross-Platform Support**: OS-specific Hiera data (RedHat.yaml, Debian.yaml) needs migration to Ansible's when conditionals and OS-specific variables

### Migration Order

1. **base_utils** (low risk, foundational) - Migrate utility functions and MOTD management first as other modules depend on these patterns
2. **profile_postgresql** (moderate complexity) - Database layer with straightforward package/service management
3. **profile_redis_cluster** (high complexity) - Requires PuppetDB query replacement and cluster coordination logic
4. **profile_app_stack** (high complexity) - Complex orchestration with custom functions and strict dependencies
5. **profile_haproxy** (highest complexity) - Most complex template logic, SSL configuration, and backend discovery
6. **role** (low complexity) - Simple composition layer, migrate after all profiles are complete

### Assumptions

- Current Puppet infrastructure uses PuppetDB for node discovery and exported resources - Ansible replacement strategy needs definition
- SSL certificates are managed externally to Puppet - certificate deployment mechanism needs clarification for Ansible
- The test Git repository setup in site.pp is for development only - production node classification method needs identification
- Hiera eyaml encryption is not in use - all secrets are currently in plaintext requiring immediate Vault migration
- The 21-level Hiera hierarchy in profile_haproxy is actively used - full hierarchy mapping may be needed vs. simplification opportunity
- Current firewall management approach (iptables vs. firewalld vs. ufw) needs clarification based on target OS versions
- Monitoring integration mentioned in profile_app_stack is not detailed - external monitoring system integration requirements need specification