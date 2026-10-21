# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef codebase with exactly two separately identifiable Chef cookbook modules: the root cookbook (`recipes/default.rb`) and the nested `cookbooks/cache` cookbook (`cookbooks/cache/recipes/default.rb`). No Puppet `manifests/init.pp` files or PowerShell `.psd1` manifests are present in the supplied repository tree. The migration is low-to-moderate complexity: the observed implementation is limited to package installation, service management, a static Nginx page, and Chef metadata/attributes. A first Ansible implementation should take about 1–2 working days, followed by 1–3 days for OS-matrix testing, dependency verification, review, and staged rollout. This estimate increases if the undeclared behavior of the external `nginx` cookbook must also be reproduced.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning.

### MODULE INVENTORY

- **simple-nginx (root Chef cookbook)**:
    - Description: Root Chef cookbook that installs Nginx, enables and starts the Nginx service, and creates a static welcome page at `/var/www/html/index.html`.
    - Path: `.`
    - Technology: Chef
    - Key Features: `nginx` package installation; `nginx` service enable/start; root-owned, mode `0644` index page; default attributes for Nginx port, user, and worker processes; metadata dependencies on the local `cache` cookbook and external `nginx` cookbook.
    - Primary entrypoint reviewed: `recipes/default.rb`

- **cache**:
    - Description: Separate local Chef cookbook providing a basic Redis cache service.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Installs the `redis-server` package and enables/starts the `redis-server` service.
    - Primary entrypoint reviewed: `cookbooks/cache/recipes/default.rb`

**CRITICAL PATH VERIFICATION:**
Both inventory entries are separate because both directories contain their own Chef primary entrypoint named `recipes/default.rb`. The root module is confirmed by `recipes/default.rb` and root `metadata.rb`; the nested module is confirmed by `cookbooks/cache/recipes/default.rb` and `cookbooks/cache/metadata.rb`. The paths `.` and `cookbooks/cache` are directories present in the repository tree. No Puppet or PowerShell modules were found in the supplied tree, so none are included in the inventory.

### Infrastructure Files

- `metadata.rb`: Root `simple-nginx` cookbook metadata. Declares Chef `>= 16.0`, version `1.0.0`, Ubuntu `>= 18.04`, CentOS `>= 7.0`, and dependencies on `cache` and external `nginx`. Convert the dependency and platform information into Ansible project documentation, role metadata, and tested requirements.
- `attributes/default.rb`: Chef defaults `nginx.port = 80`, `nginx.user = 'www-data'`, and `nginx.worker_processes = 'auto'`. Convert these to role defaults or inventory/group variables after confirming their intended use.
- `recipes/default.rb`: Root cookbook implementation. Convert to the Nginx Ansible role task entrypoint.
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata, version `1.0.0`, Chef `>= 16.0`, and Ubuntu/CentOS support declarations.
- `cookbooks/cache/recipes/default.rb`: Cache cookbook implementation. Convert to a separate Redis/cache role or a clearly isolated role dependency.
- `README.md`: Explains that this is a metadata-only dependency-strategy test and identifies `cache` as local and `nginx` as external. Retain this context in migration and test documentation.

### Target Details

- **Operating System**: The Chef metadata explicitly supports Ubuntu `>= 18.04` and CentOS `>= 7.0`. The migration should select currently supported Ubuntu and RHEL-compatible releases for testing rather than assume these historical minimums remain supported. Redis package/service naming requires OS-specific mapping.
- **Virtual Machine Technology**: Not specified. No VM provider, cloud-init, virtualization tooling, or guest-agent configuration is present.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or other cloud integration is present.

## Migration Approach

Create an Ansible project with two distinct roles, for example `roles/simple_nginx` and `roles/cache`, and a playbook that applies them in an agreed order. Use `ansible.builtin.package`, `ansible.builtin.service`/`systemd`, and `ansible.builtin.copy` or `template`. Preserve the observed idempotent outcomes: packages installed, services enabled and running, and the index file owned by `root:root` with mode `0644`.

Treat the root cookbook and `cache` as separate migration work items and code-review units. First establish the effective Chef dependency graph, then implement and test the cache role and Nginx role independently before integrating them in a playbook. Use CI or Molecule-style tests for package state, service state, file content, ownership, permissions, and platform-specific names.

### Key Dependencies to Address

- **Chef Infra `>= 16.0`**: Replace the Chef runtime with a pinned, supported `ansible-core` version and documented execution environment.
- **Local `cache` cookbook, version `1.0.0`**: Replace with the separate Ansible cache/Redis role. The visible Nginx recipe does not directly call the cache recipe, so confirm whether deployment orchestration relied on Chef metadata ordering.
- **External `nginx` cookbook**: Root metadata declares `nginx`, and `README.md` says it is external and unavailable without Berkshelf/Policy tooling. Identify its actual version and behavior before migration; do not assume the visible root recipe captures all of it. Replace required behavior with explicit Ansible tasks or a vetted Ansible role.
- **Nginx package/service**: Map the package and service names for each selected OS. Preserve enablement and startup behavior.
- **Redis package/service**: The source uses `redis-server`, which is common on Debian/Ubuntu but may differ on RHEL-family systems. Define OS-family variables and test service activation.

### Security Considerations

- **HTTP exposure**: The default Nginx port is `80`; no TLS, firewall, virtual-host restriction, or access-control configuration is present. Document that the observed behavior is cleartext HTTP and decide whether firewall/TLS controls belong in the migration scope.
- **Static file permissions**: Preserve `/var/www/html/index.html` as `root:root`, mode `0644`, and validate that the web service can read it without granting write access.
- **Redis exposure and hardening**: The cache cookbook only starts Redis and provides no bind-address, authentication, ACL, TLS, persistence, or firewall configuration. Ensure Redis is not exposed beyond trusted interfaces and define production hardening separately.
- **Platform account differences**: The attribute `nginx.user = 'www-data'` may not match CentOS/RHEL conventions. Make service-user handling OS-aware and validate permissions.
- **Secrets and certificates**: No encrypted data bags, Chef Vault references, hardcoded passwords, private keys, certificates, or environment-variable secrets are visible in the reviewed files. No per-module credentials were identified. Any newly introduced Redis credentials, TLS keys, or certificates must be stored in Ansible Vault or an approved external secrets manager.

### Technical Challenges

- **Two separate cookbook boundaries**: Do not collapse the root cookbook and `cookbooks/cache` into one Ansible role. Preserve independent ownership, testing, and release coordination.
- **External dependency uncertainty**: The declared external `nginx` cookbook is not present locally. Obtain a Chef lockfile, resolved cookbook source, catalog, or deployment record to discover behavior that is absent from the repository.
- **Cross-platform behavior**: Ubuntu and CentOS support is declared, but `redis-server` and `www-data` may not be portable. Use variable maps and test the selected OS versions.
- **Unused root attributes**: `nginx.port`, `nginx.user`, and `nginx.worker_processes` are defined in `attributes/default.rb` but are not consumed by the reviewed root recipe. Determine whether the external dependency consumed them before mapping them to active Ansible configuration.
- **Limited configuration coverage**: There are no local Nginx configuration templates, Redis configuration files, firewall rules, monitoring checks, or backups. Scope the initial migration to observed behavior and create follow-up work items for missing operational requirements.

### Migration Order

1. **Baseline and dependency discovery**: Confirm the root cookbook’s resolved `nginx` dependency and any production Chef catalog behavior.
2. **`cache` module**: Implement and test the independent Redis/cache role, including OS-specific package/service names and minimum network hardening.
3. **`simple-nginx` root module**: Implement the independent Nginx role, package/service tasks, static page, ownership, and permissions.
4. **Attribute and platform decisions**: Convert the three root attributes to documented Ansible variables only after confirming whether they affect generated Nginx configuration or external cookbook behavior.
5. **Integration and rollout**: Apply both roles through an Ansible playbook, validate against the Chef baseline, run the OS test matrix, then perform staged deployment with rollback instructions.

### Assumptions

- The root directory is one Chef cookbook, named `simple-nginx` by root `metadata.rb`; its module path is `.`.
- `cookbooks/cache` is a second, separate Chef cookbook and must have its own inventory entry and Ansible migration unit.
- The two `recipes/default.rb` files represent two modules, not duplicate files within one module.
- No Puppet `manifests/init.pp` module and no PowerShell `.psd1` module manifest exists in the supplied repository tree.
- The external `nginx` cookbook is not locally available, so its exact implementation and version remain unknown.
- The reviewed default recipes are the observable behavior to reproduce; hidden Chef roles, environments, Berkshelf files, Policyfiles, lockfiles, or deployment overrides may add behavior.
- Ubuntu `>= 18.04` and CentOS `>= 7.0` are metadata compatibility declarations, not a commitment to deploy unsupported operating-system releases.
- No cloud provider, VM technology, inventory, privilege-escalation convention, CI system, firewall policy, TLS policy, monitoring, backup, or secret-management integration is specified.
- The Redis service is intended as a simple cache, but its consumers, data-loss tolerance, persistence policy, and security requirements are undocumented.
- The implementation estimate assumes no hidden external-cookbook behavior: approximately 2–5 working days including implementation, tests, review, and rollout preparation.
- Migration owners should be assigned separately for the cache role, Nginx role, platform testing, security review, and release coordination.
