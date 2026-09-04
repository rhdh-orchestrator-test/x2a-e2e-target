# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 7 custom modules implementing a complete application stack infrastructure. The migration involves converting Puppet manifests, templates, custom functions, and Hiera data to Ansible equivalents. Estimated timeline: 6-8 weeks for a team of 2-3 engineers with moderate Puppet/Ansible experience.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helpers, MOTD management, and utility package installation with custom defined types and functions
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: MOTD template management, utility package arrays, custom defined types (config_entry, create_dir, managed_notify), Bolt tasks support

**profile**:
- Description: Profile module containing base system configurations organized by functional areas (app, base, cache, loadbalancer)
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Modular profile organization, role-profile pattern implementation, system-level configurations

**profile_app_stack**:
- Description: Complete Python application stack with PostgreSQL integration, systemd service management, and monitoring
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, Gunicorn WSGI server, systemd service hardening, custom database URL function, log rotation, environment file management

**profile_haproxy**:
- Description: HAProxy load balancer with SSL termination, backend discovery, statistics interface, and firewall integration
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend configuration via concat fragments, SSL/TLS support, statistics dashboard, firewall rule management, service discovery capabilities, custom error pages

**profile_postgresql**:
- Description: PostgreSQL 15 database server installation and configuration with repository management
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PostgreSQL 15 installation, repository configuration, service management, basic database setup

**profile_redis_cluster**:
- Description: Redis cluster configuration with password authentication and memory management
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: Redis cluster setup, password authentication, memory limits (256MB default), systemd integration

**puppetdb_query_stub**:
- Description: PuppetDB query stub library providing mock functions for testing environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Ruby library functions for PuppetDB query mocking, testing support

**role**:
- Description: Role definitions implementing the role-profile pattern for server classifications
- Path: site-modules/role
- Technology: Puppet
- Key Features: App server role (app_server.pp), application stack role (app_stack.pp), HAProxy role (haproxy.pp), Redis cluster role (redis_cluster.pp)

### Infrastructure Files

- `Puppetfile`: Puppet module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules as primary module source
- `hiera.yaml`: 5-level Hiera hierarchy (per-node, per-OS family, per-environment, common) with YAML backend
- `manifests/site.pp`: Main site manifest with test Git repository setup and node classification
- `data/common.yaml`: Global Hiera data with application configuration, database credentials, and service parameters
- `data/environment/`: Environment-specific overrides for production and staging
- `Vagrantfile`: Vagrant configuration for local development and testing
- `vagrant-provision.sh`: Vagrant provisioning script
- `test/`: Container-based testing framework with Podman/systemd integration

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 (based on metadata.json specifications across modules)
- **Virtual Machine Technology**: Not specified in repository, likely VMware or KVM based on enterprise patterns
- **Cloud Platform**: Not specified, appears to be on-premises or cloud-agnostic infrastructure

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin collection and community.general for utility functions
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble for file fragment assembly
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw depending on target OS
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module for repository management
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules and custom configuration templates
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd and ansible.builtin.template for unit files
- **puppetlabs-inifile (6.1.1)**: Replace with community.general.ini_file module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found in Hiera data requiring Ansible Vault migration:
  - HAProxy stats password: "test-haproxy-password" in data/common.yaml
  - Database password: "test-db-password" in data/common.yaml  
  - Redis password: "test-redis-password" in data/common.yaml
  - Application secret key: "test-secret-key" in data/common.yaml
- **SSL/TLS Configuration**: HAProxy SSL certificate paths and cipher configurations need secure variable handling
- **Service Hardening**: Systemd security directives (NoNewPrivileges, ProtectSystem, PrivateTmp) must be preserved in Ansible service templates
- **File Permissions**: Critical permission settings on /var/lib/haproxy, application directories, and log files require careful migration
- **Database Security**: PostgreSQL user creation and database access controls need secure credential management

### Technical Challenges

- **Custom Puppet Functions**: profile_app_stack::app_db_url Ruby function requires conversion to Jinja2 filter or Ansible module
- **Concat Fragment Assembly**: HAProxy backend configuration uses Puppet concat for dynamic fragment assembly - requires Ansible template with loops or assemble module
- **Hiera Hierarchy**: 5-level hierarchy with automatic parameter lookup needs conversion to Ansible variable precedence and group_vars structure
- **Service Dependencies**: Complex dependency chains (python -> database -> app -> service -> monitoring) require careful Ansible task ordering and handlers
- **Template Conversion**: ERB templates (.erb) and EPP templates (.epp) need conversion to Jinja2 with parameter mapping
- **Testing Framework**: Container-based Puppet testing with systemd requires equivalent Ansible testing approach using molecule or similar

### Migration Order

1. **base_utils** (low risk, foundational): Simple utility module with basic package management and MOTD - good starting point
2. **profile_postgresql** (moderate complexity): Database foundation required by application stack - clear dependencies
3. **profile_redis_cluster** (moderate complexity): Cache layer with straightforward Redis configuration
4. **profile_app_stack** (high complexity): Core application with custom functions, complex templates, and service dependencies
5. **profile_haproxy** (high complexity): Load balancer with dynamic configuration, SSL, and backend discovery
6. **profile** (low complexity): Simple profile organization module
7. **role** (low complexity): Role definitions that orchestrate profiles
8. **puppetdb_query_stub** (specialized): Testing utility, migrate last or replace with Ansible equivalents

### Assumptions

- Target environments will maintain the same OS distributions (RHEL 8/9, Ubuntu 22.04/24.04, Debian 11/12) as specified in module metadata
- Current Puppet agent infrastructure can be gradually replaced with Ansible control nodes without service disruption
- Existing Hiera data structure and hierarchy logic should be preserved in Ansible group_vars and host_vars organization
- PostgreSQL 15 version requirement will be maintained in the Ansible implementation
- Python application deployment pattern (Git clone, virtual environment, Gunicorn WSGI) should remain consistent
- HAProxy configuration complexity including SSL termination and backend discovery features must be fully preserved
- Systemd service hardening and security directives are critical requirements that cannot be simplified
- Container-based testing approach should be maintained using Ansible molecule or equivalent framework
- Environment-specific overrides (production.yaml, staging.yaml) indicate multi-environment deployment requirements
- Custom error pages and logging configurations for HAProxy are production requirements
- Database connection URL encoding logic in the custom Puppet function handles special characters and must be preserved
- Service discovery capabilities in HAProxy profile suggest dynamic infrastructure that may require additional Ansible inventory plugins
- The role-profile pattern indicates a mature infrastructure-as-code practice that should be maintained in Ansible structure
- Git repository deployment from local file:// URLs suggests air-gapped or internal development workflows
- Vagrant and container testing indicate development team familiarity with infrastructure testing that should be preserved