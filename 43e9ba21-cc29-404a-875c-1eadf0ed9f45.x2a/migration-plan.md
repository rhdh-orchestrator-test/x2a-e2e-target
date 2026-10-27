# MIGRATION FROM CHEF TO ANSIBLE

The repository is a small Chef codebase with two independently identifiable cookbooks: the root cookbook `simple-nginx` and the local `cache` cookbook. The root cookbook installs and starts Nginx and creates a static web page; the cache cookbook installs and starts Redis. The migration is low in module count and implementation complexity, but the unresolved external `nginx` dependency and cross-distribution package/service differences require validation. Estimate 2–4 engineering days for implementation and basic testing, or one sprint including multi-OS acceptance testing, security review, documentation, and team handoff.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:** The supplied repository tree contains `recipes/default.rb` at the repository root and `cookbooks/cache/recipes/default.rb`. Therefore, both directories below are separate Chef cookbook entries. The paths are directory paths that exist in the supplied tree; neither cookbook is grouped with the other.

- **simple-nginx**:
    - Description: Primary Chef cookbook that installs Nginx, enables and starts the Nginx service, and creates a static welcome page at `/var/www/html/index.html`.
    - Path: `.`
    - Technology: Chef
    - Entry point verified: `recipes/default.rb`
    - Key Features: Nginx package installation, service enablement and startup, root-owned `0644` index page, and default attributes for port, user, and worker process count.

- **cache**:
    - Description: Separate local Chef cookbook that installs Redis as a cache service and enables and starts it.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Entry point verified: `cookbooks/cache/recipes/default.rb`
    - Key Features: `redis-server` package installation and service enablement/startup; metadata support declarations for Ubuntu and CentOS.

No Puppet `manifests/init.pp` files or PowerShell `.psd1` module manifests appear in the supplied repository tree. No additional Chef cookbook directory with a `recipes/default.rb` entry point is shown.

### Infrastructure Files

- `README.md`: Identifies the repository as a metadata-only Chef dependency-strategy test and names `cache` as a local dependency and `nginx` as an external dependency. Retain this context, but confirm production requirements separately.
- `metadata.rb`: Root cookbook metadata for `simple-nginx`, including version `1.0.0`, Chef `>= 16.0`, Ubuntu `>= 18.04`, CentOS `>= 7.0`, and dependencies on `cache` and `nginx`.
- `attributes/default.rb`: Defines `default['nginx']['port'] = 80`, `user = 'www-data'`, and `worker_processes = 'auto'`. These should become Ansible role defaults or inventory variables only if they are required.
- `recipes/default.rb`: Root cookbook entry point and source for the Nginx role tasks.
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata, including version `1.0.0`, Chef `>= 16.0`, and Ubuntu/CentOS support declarations.
- `cookbooks/cache/recipes/default.rb`: Cache cookbook entry point and source for Redis package/service tasks.

### Target Details

- **Operating System**: Ubuntu `>= 18.04` and CentOS `>= 7.0` are declared. The implementation uses Linux package and service resources. Ansible should initially target tested Ubuntu and a supported RHEL-family release; RHEL 9 is a possible default but is not explicitly validated. Redis package and service names must be mapped per distribution.
- **Virtual Machine Technology**: Not specified; no VM, image, cloud-init, or hypervisor configuration is present.
- **Cloud Platform**: Not specified; no AWS, Azure, GCP, or cloud metadata configuration is present.

## Migration Approach

Create a primary Ansible role such as `simple_nginx` and a separate `cache` or `redis` role. Use a site playbook to include them explicitly. Convert the Chef package, service, and file resources into idempotent Ansible tasks, with handlers where configuration changes require service restarts. Preserve the index page owner, group, mode, and content. Use distribution-specific variables for package and service names.

The root recipe does not explicitly invoke the cache recipe, so the migration must not silently assume that Redis is installed with Nginx. Confirm whether Redis is required, then express that relationship through playbook role ordering or an explicit dependency. The external `nginx` cookbook is not present in the repository; determine its expected behavior before selecting an Ansible Galaxy role or implementing additional Nginx configuration.

### Key Dependencies to Address

- **Chef `>= 16.0`**: Replace Chef client convergence with a documented `ansible-core` version, controller requirements, and managed-node Python prerequisites.
- **Local `cache` cookbook**: Migrate `cookbooks/cache` to a separate internal Ansible role for Redis. Include it explicitly only where required.
- **External `nginx` cookbook**: Declared by `metadata.rb` but absent from the repository. Locate its original source or lock information; do not infer unreviewed functionality. If needed, replace it with approved native Ansible tasks or a pinned, reviewed collection/role.
- **Linux package/service providers**: Map `nginx`, `redis-server`, and service names per OS family instead of assuming Ubuntu naming works on CentOS/RHEL.
- **Dependency locking**: No Berksfile or Policyfile is present. Establish Ansible collection/role version pinning if external dependencies are introduced.

### Security Considerations

- **Network exposure**: The Nginx port attribute is `80`, but the recipe does not configure a listener, firewall, or TLS. Confirm intended exposure and add firewall rules only from an approved design.
- **File permissions**: Preserve `/var/www/html/index.html` as `root:root` with mode `0644`; do not broaden write access during migration.
- **Redis hardening**: The source only starts Redis. Decide whether it must bind to localhost, require authentication, use TLS, be firewalled, or have persistence disabled for cache-only use.
- **Nginx hardening**: Review the intended Nginx worker user and `worker_processes` setting before exposing the service. Add TLS and security headers only if required by the target design.
- **Secrets and credentials**: No hardcoded passwords, encrypted data bags, Chef Vault references, certificates, private keys, or environment-variable secrets were visible in the reviewed files. Any newly required Redis credentials, certificates, or upstream secrets must be stored in Ansible Vault or an approved secret manager.
- **Dependency supply chain**: Pin and review any replacement for the absent external `nginx` cookbook.

### Technical Challenges

- **Missing external dependency source**: `nginx` is declared but not included. Mitigate by recovering its source/lock data or formally scoping the migration to the behavior visible in this repository.
- **Attributes are not consumed by the reviewed recipe**: Port, user, and worker-process defaults are declared but no Nginx configuration template is present. Confirm whether they are legacy or intended future configuration before implementing them.
- **Cross-platform service naming**: Redis service/package naming may differ between Ubuntu and CentOS/RHEL. Use OS-specific variable files and test each supported family.
- **Implicit dependency semantics**: Metadata declares `cache`, but the root default recipe does not include the cache recipe. Make installation topology explicit in the Ansible playbook.
- **Limited production evidence**: This is a minimal test cookbook with no tests, templates, firewall rules, TLS, monitoring, or backup configuration shown. Conduct stakeholder acceptance testing before claiming production parity.

### Migration Order

1. Confirm the target OS matrix, whether Redis is required, and the intended behavior of the missing external `nginx` cookbook.
2. Implement and test the `cache`/Redis role with distribution-specific package and service variables.
3. Implement and test the `simple_nginx` role for Nginx package/service management and the static index page.
4. Decide whether the Chef attributes require an Nginx configuration template; add approved firewall, TLS, and hardening controls if required.
5. Compose the roles in a site playbook, run lint/syntax/idempotence and multi-OS tests, perform staged acceptance, and cut over after parity approval.

### Assumptions

- `.` is the root Chef cookbook because it contains `recipes/default.rb` and `metadata.rb`.
- `cookbooks/cache` is a separate cookbook because it contains its own `recipes/default.rb` and `metadata.rb`.
- The supplied tree is complete; no Berksfile, Policyfile, lockfile, templates, tests, or additional recipes are available.
- The root default recipe is the primary entry point, and the cache recipe is not automatically executed by the root recipe.
- The external `nginx` dependency may contain behavior not visible in this repository.
- The Chef attributes are authoritative defaults but are currently unused by the reviewed root recipe.
- Ubuntu 18.04 and CentOS 7 declarations may be historical and do not guarantee current repository or security support.
- No cloud, virtualization, inventory, firewall, TLS, monitoring, backup, or secret-management requirements are represented.
- Redis persistence, bind address, authentication, retention, and network policy are unspecified.
- The timeline assumes no hidden behavior is discovered in external dependencies or deployment wrappers.
