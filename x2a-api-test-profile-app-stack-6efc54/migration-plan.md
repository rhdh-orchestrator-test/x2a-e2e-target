# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a sophisticated Puppet control repository implementing a multi-tier application stack with HAProxy load balancing, Redis caching, and PostgreSQL database services. The migration involves 7 distinct modules using Puppet's roles-and-profiles pattern, with complex Hiera hierarchies and PuppetDB integration. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with moderate complexity due to the multi-level Hiera data structure and service discovery components.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Facter facts, Bolt tasks and plans, ERB templates for MOTD, OS-specific Hiera data

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL database, systemd service management, and strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, EPP/ERB templates for service files, logrotate configuration, health check scripts

**profile_haproxy**:
- Description: HAProxy load balancer with SSL termination, statistics interface, backend discovery, and firewall integration
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Multi-backend configuration via Hiera deep merge, SSL certificate management, custom error pages, PuppetDB-based service discovery, firewall rules

**profile_postgresql**:
- Description: PostgreSQL database server installation and configuration with repository management and service control
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: Version-specific package installation, repository configuration, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with memory management and PuppetDB-based node discovery
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster member discovery, memory policy configuration, password authentication

**profile**:
- Description: Profile wrapper classes implementing the roles-and-profiles pattern with thin delegation layers
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Environment-aware profile wrappers for base OS, cache, load balancer, and application stack components

**role**:
- Description: Role classes combining multiple profiles to define complete node configurations
- Path: site-modules/role
- Technology: Puppet
- Key Features: Multi-profile orchestration for app_server and app_stack roles with dependency management

### Infrastructure Files

- `Puppetfile`: External module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, apt, and inifile modules
- `environment.conf`: Module path configuration defining site-modules, modules, and base module paths
- `hiera.yaml`: 4-level hierarchy (per-node, per-OS, per-environment, common) with YAML data backend
- `manifests/site.pp`: Site-wide configuration with test Git repository setup and default node classification
- `data/`: Hierarchical configuration data with environment-specific overrides and OS-family variations
- `Vagrantfile`: Development environment provisioning for testing
- `test/`: Container-based testing infrastructure with Containerfile and test runner

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Debian 11/12, Ubuntu 22.04/24.04 (multi-platform support based on metadata.json specifications)
- **Virtual Machine Technology**: Not specified (development uses Vagrant, production platform unclear)
- **Cloud Platform**: Not specified (no cloud-specific configurations detected)

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

- **Hardcoded passwords**: Multiple plaintext passwords found in Hiera data (HAProxy stats, database, Redis, application secret key) - migrate to Ansible Vault
- **SSL certificate management**: HAProxy SSL configuration with certificate and key paths - implement Ansible certificate deployment with proper file permissions
- **Database credentials**: PostgreSQL connection strings with embedded passwords - use Ansible Vault for database authentication
- **SSH hardening**: SSH configuration parameters in Hiera - migrate to ansible.posix.sshd_config module
- **Service discovery**: PuppetDB queries for dynamic backend discovery - replace with Ansible inventory plugins or service registration patterns

### Technical Challenges

- **PuppetDB integration**: profile_redis_cluster and profile_haproxy use PuppetDB queries for dynamic service discovery - requires redesign using Ansible inventory plugins, service registration, or external service discovery tools
- **Complex Hiera hierarchy**: 4-level data hierarchy with deep merging - migrate to Ansible group_vars/host_vars structure with proper variable precedence
- **Custom Puppet functions**: base_utils contains custom functions (ensure_value, normalize_port, app_db_url) - reimplement as Ansible filters or lookup plugins
- **Strict dependency chains**: profile_app_stack enforces strict ordering with contain/require relationships - replicate using Ansible handlers and task dependencies
- **Multi-OS support**: OS-specific package names and paths in Hiera - implement using Ansible when conditions and OS-specific variable files
- **Template complexity**: EPP and ERB templates with complex logic - convert to Jinja2 with equivalent functionality

### Migration Order

1. **base_utils** (low risk, foundational) - Migrate utility functions, MOTD management, and package installation patterns first
2. **profile_postgresql** (moderate complexity) - Database foundation required by application stack
3. **profile_app_stack** (high complexity) - Core application deployment with Git integration and service management
4. **profile_redis_cluster** (high complexity, PuppetDB dependency) - Requires service discovery redesign
5. **profile_haproxy** (highest complexity) - Load balancer with dynamic backend discovery and SSL management
6. **profile and role** (low complexity) - Wrapper classes, migrate after underlying profiles are complete

### Assumptions

- PuppetDB service discovery can be replaced with static inventory or alternative service registration mechanisms
- SSL certificates are managed externally and can be deployed via Ansible file modules
- The test Git repository setup in site.pp is for development only and may not need migration
- Current Hiera data represents production-ready configuration values that should be preserved
- The multi-platform support (RHEL/Debian/Ubuntu) requirement will be maintained in Ansible
- Vagrant-based development workflow can be replaced with Ansible-based local testing
- External module dependencies have equivalent Ansible collections or can be implemented with core modules
- The roles-and-profiles pattern will be adapted to Ansible's role and playbook structure
- Database schema migrations (Alembic) are handled by the application and don't require Puppet/Ansible management