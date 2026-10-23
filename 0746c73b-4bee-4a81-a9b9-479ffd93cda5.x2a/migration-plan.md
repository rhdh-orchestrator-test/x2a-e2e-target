# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef cookbook infrastructure that demonstrates a metadata-only dependency strategy with a main nginx web server cookbook and a local cache dependency. The migration scope is relatively small with 2 cookbooks total, making this a low-to-medium complexity migration. Estimated timeline: **2-3 weeks** including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Nginx web server installation and configuration with basic HTML content delivery, supports Ubuntu 18.04+ and CentOS 7+
    - Path: . (root directory)
    - Technology: Chef
    - Key Features: Package installation via system package manager, service management (enable/start), static HTML file creation, configurable worker processes and port settings
    - Chef Version: >= 16.0

- **cache**:
    - Description: Redis server installation and configuration for caching services, supports Ubuntu 18.04+ and CentOS 7+
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation via system package manager, service management (enable/start)
    - Chef Version: >= 16.0

### Infrastructure Files

- `metadata.rb` (root): Main cookbook metadata declaring dependencies on 'cache' (local) and 'nginx' (external community cookbook)
- `attributes/default.rb`: Default configuration attributes for nginx (port, user, worker_processes)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with no external dependencies
- `README.md`: Documentation explaining metadata-only dependency strategy for X2A Convertor testing

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (dual platform support declared in metadata)
- **Virtual Machine Technology**: Not specified in configuration files
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (community cookbook)**: The root cookbook declares a dependency on the Chef Supermarket 'nginx' cookbook, but this dependency is not actively used in the recipes - the cookbook installs nginx directly via package resource. For Ansible migration, use the `ansible.builtin.package` and `ansible.builtin.service` modules, or consider the `nginxinc.nginx` Ansible Galaxy role if more advanced nginx features are needed in the future.

- **redis-server (system package)**: The cache cookbook installs redis-server via system package manager. For Ansible migration, use `ansible.builtin.package` module with appropriate package names per OS family (redis-server for Debian/Ubuntu, redis for RHEL/CentOS).

- **cache (local cookbook dependency)**: The simple-nginx cookbook depends on the cache cookbook. In Ansible, this relationship should be maintained by ensuring the cache role runs before or alongside the nginx role, managed through playbook play ordering or role dependencies.

### Security Considerations

- **No secrets management detected**: The current implementation does not use Chef Vault, encrypted data bags, or environment variables for secrets. No hardcoded credentials were found in the reviewed files.
- **File permissions**: The nginx index.html file is created with mode '0644' and root ownership, which is appropriate for public web content. Ansible migration should maintain these permissions using the `ansible.builtin.file` module.
- **Service exposure**: Both nginx (port 80 configurable) and redis will be exposed. Migration should include:
  - Firewall configuration considerations (not currently defined in Chef code)
  - Redis binding configuration review (default may bind to all interfaces)
  - SSL/TLS termination strategy for nginx (not currently implemented)
- **Package verification**: Consider adding package signature verification in Ansible playbooks for enhanced security posture.

### Technical Challenges

- **Package name differences across distributions**: The cache cookbook uses 'redis-server' as the package name, which is Debian/Ubuntu-specific. CentOS/RHEL uses 'redis'. The Ansible migration must use conditional package names based on `ansible_os_family`:
  ```yaml
  package:
    name: "{{ 'redis-server' if ansible_os_family == 'Debian' else 'redis' }}"
  ```
  Similarly, service names may differ and need to be handled conditionally.

- **Service name variations**: Redis service names differ between platforms (redis-server vs redis). Ansible roles should use variables to manage these differences.

- **Nginx community cookbook dependency ambiguity**: The metadata declares a dependency on the 'nginx' cookbook but doesn't use it in recipes. During migration, clarify whether this was intentional for future use or if it can be removed. Document the decision to avoid confusion.

- **Attribute translation**: Chef attributes use nested hash structure (`node['nginx']['port']`). Ansible should use role defaults with similar namespacing for consistency:
  ```yaml
  nginx_port: 80
  nginx_user: www-data
  nginx_worker_processes: auto
  ```

- **Metadata-only strategy testing**: The README indicates this is a test repository for "X2A Convertor" validation. Coordinate with the testing team to understand what validation requirements the migrated Ansible roles must meet.

### Migration Order

1. **cache cookbook** (Priority 1: No dependencies, straightforward service installation)
   - Low risk: Simple package and service management
   - High value: Required dependency for nginx cookbook
   - Estimated effort: 2-3 days including testing across both Ubuntu and CentOS

2. **simple-nginx cookbook** (Priority 2: Depends on cache, moderate complexity)
   - Moderate complexity: Multiple resources (package, service, file, attributes)
   - Cross-platform considerations for both cookbooks
   - Estimated effort: 4-5 days including multi-platform testing and documentation
   - Should include creation of templates for nginx configuration if future customization is needed

3. **Integration testing** (Priority 3: Validate cookbook interaction)
   - Test cache and nginx working together
   - Validate on both Ubuntu 18.04+ and CentOS 7+ targets
   - Estimated effort: 3-4 days for comprehensive testing and documentation

### Assumptions

- **Berkshelf/Policyfile absence**: No Berksfile or Policyfile.rb was found, indicating this repository uses a metadata-only dependency resolution strategy. The external 'nginx' community cookbook dependency declared in metadata.rb may not be resolved or used in practice. We assume this dependency can be ignored during migration since the recipes implement nginx installation directly.

- **Chef Server vs Chef Solo/Zero**: The repository structure doesn't indicate whether this runs on Chef Server, Chef Solo, or Chef Zero. We assume the Ansible migration will target direct SSH-based execution via ansible-playbook, not requiring a central Ansible Tower/AWX server unless specified later.

- **Target environment homogeneity**: While the cookbooks support both Ubuntu and CentOS, we assume test/production environments are likely homogeneous (all Ubuntu or all CentOS), not mixed. If mixed environments exist, additional inventory grouping and testing will be required.

- **Redis configuration defaults**: The cache cookbook installs redis with default configurations. We assume default redis.conf settings are acceptable and no custom configuration file management is required. If custom Redis configuration is needed (bind address, memory limits, persistence settings), this should be clarified before migration.

- **Nginx content management**: The simple-nginx cookbook creates a single static index.html file. We assume this is for testing/demonstration only and production use cases will require either:
  - Template-based content management
  - External content deployment processes
  - Integration with application deployment workflows
  
  The migration should clarify the intended content management strategy.

- **No load balancing or clustering**: Neither cookbook implements high availability, load balancing, or clustering configurations. We assume single-node deployments are the target. If HA/clustering is required, this represents additional scope.

- **Service restart/reload behavior**: Chef service resources use :enable and :start actions. We assume Ansible roles should implement similar idempotent behavior (start if not running, enable at boot) without automatic restarts on configuration changes unless explicitly requested.

- **No monitoring or logging integration**: The cookbooks don't configure monitoring agents, log shipping, or observability tools. We assume these concerns are handled separately or will be added as additional Ansible roles outside this migration scope.

- **File path assumptions**: The nginx cookbook creates /var/www/html/index.html, assuming default Debian/Ubuntu nginx document root. CentOS nginx uses /usr/share/nginx/html by default. Migration should address this platform difference or document the requirement for consistent nginx configuration.

- **User/group existence**: The nginx cookbook sets file ownership to root:root and references www-data user in attributes. We assume these users/groups exist on target systems. The Ansible migration should verify or create necessary service users.

- **No existing Ansible infrastructure**: We assume this is a greenfield Ansible migration without existing Ansible roles or playbooks to integrate with. If existing Ansible infrastructure exists, additional coordination and standardization will be required.
