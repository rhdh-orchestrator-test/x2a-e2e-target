# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook setup consisting of a main nginx cookbook with a local dependency on a cache cookbook. The migration scope is relatively small with two cookbooks managing basic web server and caching infrastructure. The migration is estimated to take 1-2 weeks for a single engineer, including testing and validation.

**Complexity Level**: Low to Medium
- 2 cookbooks with straightforward functionality
- No encrypted data bags or Chef Vault usage detected
- Standard package management and service control patterns
- One external dependency (nginx community cookbook) that needs replacement
- No complex templates or advanced Chef features observed

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths listed below have been confirmed to exist in the repository structure.

- **simple-nginx**:
    - Description: Main nginx web server installation cookbook with basic configuration for nginx package installation, service management, and simple HTML page deployment
    - Path: . (root directory)
    - Technology: Chef
    - Key Features: nginx package installation, service enablement and startup, static HTML index page creation at /var/www/html/index.html
    - Version: 1.0.0
    - Supported Platforms: Ubuntu >= 18.04, CentOS >= 7.0
    - Chef Version Requirement: >= 16.0

- **cache**:
    - Description: Redis cache server installation and management cookbook providing basic caching infrastructure
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: redis-server package installation, service enablement and startup
    - Version: 1.0.0
    - Supported Platforms: Ubuntu >= 18.04, CentOS >= 7.0
    - Chef Version Requirement: >= 16.0

### Infrastructure Files

- `metadata.rb` (root): Main cookbook metadata declaring dependencies on 'cache' (local) and 'nginx' (external community cookbook)
- `recipes/default.rb` (root): Main nginx installation recipe with package, service, and file resources
- `attributes/default.rb` (root): Default nginx configuration attributes (port: 80, user: www-data, worker_processes: auto)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support declarations
- `cookbooks/cache/recipes/default.rb`: Redis installation recipe with package and service resources
- `README.md`: Documentation describing the cookbook purpose and metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (based on metadata.rb platform support declarations). The cookbook is designed to work across both Debian and Red Hat families. Default target for Ansible migration should be Red Hat Enterprise Linux 9 unless specific Ubuntu requirements are identified.
- **Virtual Machine Technology**: Not specified in the repository. No VM-specific configurations, cloud-init files, or virtualization tools detected.
- **Cloud Platform**: Not specified. No cloud provider-specific configurations (AWS, Azure, GCP) detected in the analyzed files.

## Migration Approach

### Key Dependencies to Address

- **nginx (community cookbook)**: The main cookbook declares a dependency on the external 'nginx' community cookbook from Chef Supermarket, though it's not actively used in the default recipe. Replace with Ansible nginx role from Ansible Galaxy (e.g., `geerlingguy.nginx`) or create custom tasks using package and service modules.
- **cache (local cookbook)**: Internal dependency already present in the repository. This will be migrated as a separate Ansible role alongside the main nginx role.
- **redis-server package**: Both Ubuntu and CentOS package managers provide this. Ansible's `package` module will handle cross-platform compatibility, or use distribution-specific modules (`apt`, `yum`/`dnf`) as needed.

### Security Considerations

- **No Secrets Management Detected**: No Chef Vault, encrypted data bags, or credential patterns were found in the analyzed files. The cookbooks use standard package management and service control without authentication or credential handling.
- **File Permissions**: The nginx index.html file is created with mode '0644' and owner/group 'root'. This pattern should be preserved in Ansible using `mode`, `owner`, and `group` parameters in the `file` or `template` modules.
- **Service Security**: Default nginx and redis configurations are used without custom security hardening (SSL/TLS, authentication, access controls). Consider adding security enhancements during migration:
  - Implement firewall rules for nginx (port 80/443)
  - Configure redis to bind to localhost only
  - Add SELinux contexts if targeting RHEL-based systems
  - Consider SSL certificate management for production use
- **Attribute-Based Configuration**: The nginx attributes (port, user, worker_processes) are currently stored in `attributes/default.rb`. These should be migrated to Ansible variables in `defaults/main.yml` or group_vars/host_vars for environment-specific overrides.

### Technical Challenges

- **Package Name Differences**: The 'redis-server' package name is Debian/Ubuntu-specific. On Red Hat/CentOS, the package is named 'redis'. Ansible migration should use conditional logic or the generic `package` module to handle cross-platform compatibility:
  ```yaml
  - name: Install Redis
    package:
      name: "{{ 'redis-server' if ansible_os_family == 'Debian' else 'redis' }}"
      state: present
  ```
  
- **Service Name Variations**: Similarly, the Redis service name may differ across distributions ('redis-server' vs 'redis'). Use `ansible_os_family` or distribution-specific variables to handle this.

- **Nginx User Differences**: The attribute defaults to 'www-data' (Debian convention), but Red Hat systems use 'nginx'. The migration should detect the appropriate user based on the target OS:
  ```yaml
  nginx_user: "{{ 'www-data' if ansible_os_family == 'Debian' else 'nginx' }}"
  ```

- **Default Document Root**: The recipe creates files in `/var/www/html/`, which is the default for Ubuntu/Debian. Red Hat-based systems typically use `/usr/share/nginx/html/`. Path handling needs to be OS-aware.

- **External Dependency Resolution**: The 'nginx' community cookbook dependency in metadata.rb suggests there may be additional functionality expected from that cookbook. Since the default recipe doesn't include_recipe 'nginx', it's unclear if this dependency is actually needed. Verify whether the external cookbook was intended for future use or if it can be safely removed during migration.

- **Idempotency Verification**: Ensure Ansible playbooks maintain Chef's idempotent behavior. The package and service resources should map directly to Ansible's `package`, `service`, and `file` modules with similar idempotency guarantees.

### Migration Order

1. **cache cookbook** (Low risk, foundational dependency)
   - Simple redis installation with no complex logic
   - No external dependencies
   - Required by the main nginx cookbook
   - Estimated effort: 2-3 hours
   - Create Ansible role: `roles/cache/`
   - Test independently before integrating

2. **simple-nginx cookbook** (Low-Medium risk, depends on cache)
   - Straightforward nginx installation and configuration
   - Depends on the cache role being migrated first
   - Need to resolve external 'nginx' dependency question
   - Estimated effort: 4-6 hours
   - Create Ansible role: `roles/simple_nginx/` or `roles/nginx/`
   - Include cache role as a dependency in meta/main.yml

3. **Integration Testing** (Medium priority)
   - Test both roles together to ensure cache and nginx work correctly
   - Validate cross-platform compatibility (Ubuntu vs CentOS/RHEL)
   - Verify service startup order and dependencies
   - Estimated effort: 3-4 hours

### Assumptions

1. **External Dependency Intent**: The 'nginx' community cookbook is declared as a dependency in metadata.rb but not used in recipes/default.rb. Assuming this is either vestigial from earlier development or intended for future expansion. Migration plan assumes basic nginx functionality only, unless stakeholders confirm additional requirements from the community cookbook.

2. **No Berkshelf or Policyfile**: No Berksfile or Policyfile.rb was found in the repository, suggesting dependencies may not have been actively managed or the cookbook is used in a simpler chef-solo/chef-zero environment. This simplifies migration as there are no complex dependency resolution workflows to replicate.

3. **Testing Strategy**: The README mentions this is "for testing metadata-only dependency strategy" and is designed as a "test cookbook." Assuming this is a proof-of-concept or test environment, not production-critical infrastructure. If this is production code, additional security hardening and high-availability considerations should be added.

4. **Attribute Usage**: The nginx attributes defined in attributes/default.rb (port, user, worker_processes) are not referenced in the default recipe. Assuming these were intended for future nginx.conf template customization. Migration should preserve these as Ansible variables even though they're not currently consumed.

5. **Default Recipe Scope**: Both cookbooks only have a default.rb recipe with no additional recipes, library helpers, or custom resources. Assuming the entire functionality of each cookbook is contained in these default recipes.

6. **Platform Support Scope**: Both cookbooks support Ubuntu >= 18.04 and CentOS >= 7.0. Assuming the target environment will continue to use these distributions or their modern equivalents (Ubuntu 20.04/22.04, RHEL 8/9, Rocky Linux, AlmaLinux).

7. **No Template Files**: No ERB templates were found in the repository. The only file creation is a simple static HTML file with inline content. Assuming no complex configuration file templating is required.

8. **Service Management**: Both cookbooks use standard systemd service management (action [:enable, :start]). Assuming target systems use systemd, which is standard for Ubuntu 18.04+ and CentOS 7+.

9. **No Data Bags or Environment Files**: No Chef data bags, environment files, or role files were found. Assuming all configuration is self-contained in attributes and recipes, simplifying the migration to Ansible's inventory and variables system.

10. **Redis Configuration**: The cache cookbook installs redis-server with default configuration and no customization. Assuming default Redis settings are acceptable (no persistence configuration, memory limits, or replication setup required).

11. **Network Configuration**: No firewall rules, iptables configuration, or network security settings were found. Assuming network security is handled at a different layer (cloud security groups, external firewall appliance) or needs to be added during migration.

12. **HTML Content Management**: The index.html file has static inline content. Assuming this is placeholder content. If dynamic content or templates are needed in production, this should be replaced with Ansible's `template` module and a Jinja2 template.

13. **Chef Version Compatibility**: Both cookbooks specify Chef >= 16.0. Assuming the current environment is using a relatively recent Chef version, which means modern resource syntax is used (no legacy compatibility concerns).

14. **No Integration with Chef Server**: No knife.rb, client.rb, or Chef Server configuration files were found. Assuming this is a standalone cookbook repository that may have been used with chef-solo or chef-zero, making the migration to Ansible's agentless architecture straightforward.
