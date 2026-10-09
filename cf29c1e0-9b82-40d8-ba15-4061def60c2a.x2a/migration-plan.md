# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a well-structured Puppet control repository with 5 profile modules and 1 utility module that manage a complete application stack infrastructure. The migration involves converting role-based node classification, Hiera data hierarchies, and profile-based architecture to Ansible equivalents. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with 2 weeks for planning, 4 weeks for core migration, and 2 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Bolt tasks and plans, platform-specific Hiera data, custom facts via Facter

**profile_app_stack**:
- Description: Complete Python application stack orchestrator with PostgreSQL database, systemd service management, and strict dependency chain enforcement
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, environment-specific configuration templates, logrotate integration, health check scripts

**profile_haproxy**:
- Description: HAProxy load balancer profile with SSL termination, multi-backend support, PuppetDB service discovery, and comprehensive firewall management
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, dynamic backend discovery via PuppetDB queries, SSL/TLS configuration, stats interface, custom error pages

**profile_postgresql**:
- Description: PostgreSQL database server installation with PGDG repository management and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository management, version-specific package installation, service lifecycle management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery, memory management, and cluster-aware configuration
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster member discovery, custom Facter facts for Redis role detection, memory policy configuration

**role**:
- Description: Role-based node classification providing app_server, app_stack, haproxy, and redis_cluster roles with profile composition
- Path: site-modules/role
- Technology: Puppet
- Key Features: Profile composition pattern, Linux-specific exec path defaults, dependency ordering between base and specialized profiles

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules precedence over Forge modules
- `hiera.yaml`: 4-level hierarchy (node-specific, OS family, environment, common) with YAML backend
- `data/common.yaml`: Environment-wide defaults including hardcoded passwords and configuration values
- `data/environment/`: Environment-specific overrides for production and staging
- `manifests/site.pp`: Main site manifest for node classification (not present in tree, likely minimal)
- `Vagrantfile`: Local development environment configuration
- `test/`: Containerized testing framework with Docker/Podman support

### Target Details

- **Operating System**: Red Hat Enterprise Linux 9 and Ubuntu 24.04 LTS (based on metadata.json operatingsystem_support across modules)
- **Virtual Machine Technology**: Not specified in configuration files
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general collections for common utilities
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw modules
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module for repository management
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis configuration tasks
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hardcoded Passwords**: Multiple plaintext passwords found in data/common.yaml including HAProxy stats password, database password, Redis password, and application secret key - migrate to Ansible Vault
- **SSL/TLS Configuration**: HAProxy SSL certificate and key paths configured but SSL disabled by default - ensure proper certificate management in Ansible
- **Database Credentials**: PostgreSQL and application database credentials stored in Hiera - implement Ansible Vault encryption
- **SSH Hardening**: SSH configuration parameters in common.yaml need migration to ansible.posix.sshd_config module
- **Service Account Management**: Application user/group creation patterns need migration to ansible.builtin.user and ansible.builtin.group modules

### Technical Challenges

- **PuppetDB Queries**: profile_haproxy and profile_redis_cluster use PuppetDB queries for dynamic service discovery - replace with Ansible inventory plugins or dynamic inventory scripts
- **Custom Puppet Functions**: base_utils module contains custom functions (ensure_value, normalize_port) and profile_app_stack has app_db_url function - reimplement as Ansible filters or lookup plugins
- **Hiera Hierarchy**: Complex 4-level hierarchy with node, OS, environment, and common data - migrate to Ansible group_vars and host_vars structure
- **Dependency Ordering**: Strict dependency chains using Puppet's -> and ~> operators - implement with Ansible handlers and task dependencies
- **Cross-Platform Support**: OS-specific data in base_utils for Debian/RedHat families - use Ansible when conditions and OS-specific variable files
- **Template Complexity**: ERB templates with conditional logic based on facts['environment'] - convert to Jinja2 templates with Ansible variables

### Migration Order

1. **base_utils** (low risk, foundational): Utility functions, MOTD, package management - establishes common patterns
2. **profile_postgresql** (moderate complexity): Database installation, repository management - enables application stack
3. **profile_app_stack** (high complexity): Application deployment, service management, database integration - core business logic
4. **profile_redis_cluster** (high complexity): Cluster configuration, PuppetDB dependency - requires inventory solution
5. **profile_haproxy** (highest complexity): Load balancer, SSL, service discovery, firewall - depends on backend services
6. **role** (low risk): Node classification - final integration layer

### Assumptions

- The site.pp manifest contains minimal node classification logic since it's not present in the repository tree
- Production and staging environments use the same infrastructure patterns with different parameter values
- The Vagrant environment is used for local development and testing, not production deployment
- PuppetDB is available in the current environment for service discovery queries
- SSL certificates are managed externally and referenced by file paths in HAProxy configuration
- The application stack assumes a single-node PostgreSQL deployment based on localhost database host configuration
- Redis cluster configuration suggests multi-node deployment but specific cluster topology is not defined in the visible configuration
- The testing framework in test/ directory uses containerization for module validation
- Git repositories for application deployment are accessible from target nodes
- Firewall management is currently disabled (firewall_provider: "none") but firewall rules are defined for future use
- The migration will maintain the same role-based architecture using Ansible playbooks and roles
- Environment-specific configuration will be migrated to Ansible inventory group variables
- Custom facts and functions will need reimplementation as Ansible plugins or filters