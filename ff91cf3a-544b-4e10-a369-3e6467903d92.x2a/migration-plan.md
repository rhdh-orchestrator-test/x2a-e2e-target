# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure automation codebase consisting of two cookbooks: a main nginx web server cookbook and a local cache dependency cookbook. The migration is relatively straightforward with low to moderate complexity, involving basic package installations, service management, and file deployment. Estimated timeline: 2-3 weeks for complete migration, testing, and validation, with an additional 1-2 weeks for team knowledge transfer and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Nginx web server installation with basic configuration, service management, and custom welcome page deployment. Configurable worker processes, port, and user settings via attributes
- Path: recipes/default.rb (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement and startup, static HTML file deployment, attribute-based configuration for port, user, and worker processes

**cache**:
- Description: Redis cache server installation and service management for caching support
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis server package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb` (root): Main cookbook metadata declaring dependencies on 'cache' (local) and 'nginx' (external), supporting Ubuntu 18.04+ and CentOS 7.0+, Chef 16.0+
- `attributes/default.rb`: Default attribute definitions for nginx configuration (port: 80, user: www-data, worker_processes: auto)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support declarations

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for Ansible playbooks unless specific Ubuntu requirements exist.
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified - appears to be platform-agnostic infrastructure code suitable for any deployment environment

## Migration Approach

### Key Dependencies to Address

- **nginx (external dependency)**: Replace with Ansible `ansible.builtin.package` module for nginx installation, or use community collection `nginxinc.nginx` for advanced nginx management features. The current Chef cookbook uses a basic package installation approach, so the builtin package module should suffice.
- **redis-server (cache cookbook)**: Replace with Ansible `ansible.builtin.package` and `ansible.builtin.service` modules, or consider `community.general.redis` module for advanced Redis configuration
- **Chef >= 16.0**: Remove Chef-specific infrastructure. Ansible 2.9+ or Ansible Core 2.12+ recommended for migration target

### Security Considerations

- **No secrets detected**: No Chef Vault, encrypted data bags, or hardcoded credentials found in the reviewed files. The cookbooks use basic package installation and service management without authentication configuration.
- **File permissions**: Static HTML file deployed with explicit mode '0644' and ownership (root:root). Ensure Ansible equivalent maintains secure permissions using `mode`, `owner`, and `group` parameters in `ansible.builtin.file` or `ansible.builtin.copy` modules.
- **Service management**: Services enabled and started without explicit security hardening. Consider adding security best practices in Ansible migration (e.g., nginx configuration for security headers, Redis bind address restrictions).
- **Default credentials**: Redis installed without authentication configuration. Recommend adding Redis password authentication in the Ansible migration for production environments.

### Technical Challenges

- **External nginx dependency**: The metadata.rb declares a dependency on an external 'nginx' cookbook that is not present in the repository. This dependency strategy assumes Berkshelf or Policyfile resolution. In Ansible migration, this external dependency is unnecessary since the simple-nginx cookbook already handles nginx package installation directly. The external dependency declaration can be safely removed.
- **Platform-specific package names**: The cache cookbook uses 'redis-server' which is the Ubuntu/Debian package name. On CentOS/RHEL, the package is named 'redis'. Ansible migration should use conditional logic based on `ansible_os_family` to handle cross-platform compatibility, or use the `community.general.redis` module which abstracts platform differences.
- **Service name variations**: Similar to package names, service names may vary across platforms. Use Ansible facts and conditionals to ensure proper service management across Ubuntu and CentOS targets.
- **Attribute to variable mapping**: Chef attributes (node['nginx']['port'], etc.) need migration to Ansible variables (ansible_nginx_port, etc.). Create a clear variable naming convention and document the mapping for team reference.

### Migration Order

1. **cache cookbook** (Priority 1: Low risk, no dependencies, simple package + service management): Migrate first as a proof of concept. This establishes the pattern for package installation and service management that will be reused.
2. **simple-nginx cookbook** (Priority 2: Depends on cache, moderate complexity): Migrate after cache cookbook. Includes attribute handling, file deployment, and inter-cookbook dependency demonstration.
3. **Integration testing** (Priority 3: Validate complete stack): After both cookbooks are migrated, validate the full stack with both nginx and redis running together, simulating the original Chef cookbook dependency chain.

### Assumptions

- **Chef Server or Chef Solo**: The repository structure suggests Chef Solo or local cookbook usage (cookbooks/ subdirectory pattern). No Berksfile or Policyfile present, indicating the external 'nginx' dependency in metadata.rb may be aspirational or handled by an external dependency resolution mechanism not present in this repository.
- **Target OS choice**: While metadata.rb supports both Ubuntu 18.04+ and CentOS 7.0+, the actual target deployment platform is unclear. The cache cookbook uses 'redis-server' (Debian/Ubuntu naming), suggesting Ubuntu may be the primary target. Clarify with operations team whether to prioritize Ubuntu or CentOS compatibility in Ansible migration.
- **Nginx configuration**: The current cookbook installs nginx but does not deploy custom nginx.conf or virtual host configurations. The only customization is the simple index.html file. Clarify whether production environments require additional nginx configuration (SSL/TLS, virtual hosts, upstream proxies, etc.) that should be added during migration.
- **Redis configuration**: Redis is installed with default configuration and no authentication. Clarify whether production requires:
  - Password authentication (requirepass)
  - Bind address restrictions
  - Persistence configuration (RDB/AOF)
  - Memory limits (maxmemory, maxmemory-policy)
- **Execution environment**: No information about whether this runs in development, staging, or production environments. Different environments may require different variable values, secrets management approaches, and testing strategies.
- **Static HTML content**: The index.html content is hardcoded in the recipe. Clarify whether this is placeholder content for testing or if production requires template-based content generation with dynamic values.
- **Worker process configuration**: The attribute sets nginx worker_processes to 'auto'. Verify this is appropriate for target environments or if explicit CPU-based tuning is required.
- **User and group management**: The nginx user attribute defaults to 'www-data' (Ubuntu convention). CentOS uses 'nginx' as the default user. Clarify cross-platform user management requirements.
- **Port configuration**: Default port is 80. Clarify whether production requires configurable ports, SSL/TLS on port 443, or non-standard port configurations for security or multi-tenancy.
