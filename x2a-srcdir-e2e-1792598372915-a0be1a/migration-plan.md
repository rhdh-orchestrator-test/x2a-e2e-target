# MIGRATION FROM CHEF TO ANSIBLE

This is a small Chef repository containing one primary cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The implementation is intentionally simple and is described as a metadata-only dependency-strategy test. The migration is low complexity: approximately 1–3 engineering days for the first Ansible implementation, plus validation on each supported operating system and a short handover/documentation cycle. The main coordination point is replacing Chef cookbook dependency resolution with explicit Ansible role/collection dependencies and deciding whether the external `nginx` dependency is required beyond the currently visible recipe.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Primary cookbook that installs and enables Nginx, publishes a static welcome page, and defines default Nginx settings for port, user, and worker processes.
    - Path: `.`
    - Technology: Chef
    - Key Features: `nginx` package installation, enabled/running `nginx` service, root-owned `/var/www/html/index.html`, default attributes for port 80, `www-data`, and automatic worker-process selection.

- **cache**:
    - Description: Local dependency cookbook that installs Redis as a basic caching service and enables it at boot.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: `redis-server` package installation and enabled/running `redis-server` service.

**CRITICAL PATH VERIFICATION:**
The paths above were taken directly from the supplied repository tree. The root cookbook is identified by `metadata.rb`, `recipes/default.rb`, and `attributes/default.rb`; `cookbooks/cache` has its own `metadata.rb` and `recipes/default.rb`.

### Infrastructure Files

- `README.md`: Documents that this is a simple Nginx cookbook and a test of metadata-only dependency handling. It identifies `cache` as a local dependency and `nginx` as an external dependency that is declared but not fetchable without Berkshelf or Policyfile tooling. Migration consideration: preserve this dependency boundary in the Ansible design documentation and clarify whether external Nginx role functionality is actually needed.
- `metadata.rb`: Root Chef cookbook metadata, including cookbook identity, Chef version requirement, supported platforms, and dependencies on `cache` and `nginx`. Migration consideration: translate platform support into Ansible distribution variables and replace dependency declarations with role requirements or an internal role.
- `attributes/default.rb`: Chef default attributes for Nginx port, user, and worker-process behavior. Migration consideration: map these to role defaults, while ensuring the values are actually consumed by the Nginx configuration role.
- `recipes/default.rb`: Root convergence logic for Nginx installation, service state, and static content. Migration consideration: split into Ansible tasks/handlers and use idempotent modules such as `ansible.builtin.package`, `service`, and `copy` or `template`.
- `cookbooks/cache/metadata.rb`: Metadata for the local Redis cookbook, including Chef version and supported operating systems. Migration consideration: become an independent Ansible role with documented distribution-specific package and service names.
- `cookbooks/cache/recipes/default.rb`: Redis package and service convergence logic. Migration consideration: become a small `cache`/`redis` role with package and service tasks and validation.

No Berksfile, Policyfile, lock file, encrypted data bag, Hiera-like data source, templates directory, static file directory, or explicit environment configuration is present in the supplied tree.

### Target Details

- **Operating System**: The Chef metadata explicitly supports Ubuntu `>= 18.04` and CentOS `>= 7.0`. Package and service names are written using Debian/RHEL-compatible assumptions, but the repository does not specify exact tested versions. Ansible should initially target Ubuntu 18.04+ and CentOS 7+ compatibility, then establish a supported baseline; for a current deployment standard, validate on Ubuntu LTS and RHEL-compatible 9 systems rather than assuming legacy CentOS 7 behavior.
- **Virtual Machine Technology**: Not specified. No cloud-init, hypervisor tooling, or VM-provider configuration is present.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef `>= 16.0`**: Remove the Chef runtime dependency. Implement the behavior in an Ansible project using a pinned `ansible-core` version and a documented execution environment.
- **Local `cache` cookbook, version 1.0.0**: Convert to an internal Ansible role, likely named `redis` or `cache`, and call it from the site playbook before or alongside the Nginx role as required by the deployment architecture.
- **External `nginx` cookbook dependency**: The root metadata declares `nginx`, but the visible recipe installs Nginx directly and does not show a call to a dependency recipe. Determine whether the declaration is only a test fixture or represents required behavior. If needed, replace it with an audited internal role or a pinned Ansible Galaxy collection/role; do not import an unpinned external role.
- **Ubuntu/CentOS package and service naming**: Use distribution-aware variables. Confirm whether Redis is `redis-server` on Ubuntu and `redis`/another package-service combination on the intended RHEL-compatible target.
- **Chef resources**: Map `package`, `service`, and `file` resources to `ansible.builtin.package`, `ansible.builtin.service`, and `ansible.builtin.copy`/`template`, with handlers where configuration changes require service reloads.

### Security Considerations

- **Nginx static content**: The index file is explicitly owned by `root:root` with mode `0644`. Preserve least-privilege ownership and permissions, and review whether the content is only a test page before production rollout.
- **Service exposure**: The declared Nginx port is 80. Confirm firewall policy, listen addresses, reverse-proxy requirements, and whether HTTP should redirect to HTTPS. The source contains no firewall or TLS configuration.
- **Redis exposure**: The cache cookbook only starts Redis; it does not show bind-address restrictions, authentication, TLS, persistence, or firewall rules. The Ansible role must bind Redis appropriately (normally localhost or a restricted network), prevent unintended external access, and define security/persistence requirements explicitly.
- **Secrets and credentials**: No hardcoded passwords, API keys, encrypted data bags, vault references, certificates, private keys, or environment-variable secrets are visible in the reviewed files. Do not infer that secrets are unnecessary; document any runtime credentials discovered during deployment and store them in Ansible Vault or an approved external secret manager.
- **Supply-chain controls**: Pin Ansible collections/roles and validate any replacement for the declared external `nginx` cookbook. Add review and checksum/version controls to the execution-environment build.

### Technical Challenges

- **Underspecified dependency behavior**: `nginx` is declared in metadata but no Berksfile/Policyfile or fetched dependency is present, and the visible recipe does not invoke it. Mitigation: confirm intended dependency semantics with the owners before implementation and test the resulting service behavior independently.
- **Cross-distribution service names**: Redis and Nginx package/service names can differ between Ubuntu and CentOS/RHEL families. Mitigation: use OS-family variables, molecule tests, and explicit support boundaries rather than relying on one literal name.
- **Unused Chef attributes**: `nginx.port`, `nginx.user`, and `nginx.worker_processes` are defined but the shown recipe does not render an Nginx configuration. Mitigation: preserve them as role defaults only if configuration ownership is intended; otherwise mark them as legacy and avoid creating misleading variables.
- **Configuration completeness**: The source installs services but does not manage Nginx configuration, firewalling, Redis hardening, monitoring, or backup/persistence. Mitigation: scope the first migration to behavioral equivalence and create separate requirements for production hardening.
- **Legacy platform support**: CentOS 7 and Ubuntu 18.04 are old platform baselines. Mitigation: establish a supported target matrix and avoid promising compatibility without CI validation.
- **Validation gap**: The repository has no visible tests. Mitigation: add Molecule or equivalent integration tests covering package installation, service state, page content, permissions, idempotence, and Redis network exposure.

### Migration Order

1. **Repository and platform baseline**: Confirm target distributions, Ansible version, inventory conventions, execution environment, and whether the declared external Nginx dependency is required.
2. **`cache` role**: Migrate the small Redis cookbook first. It is isolated and provides a low-risk pattern for package/service tasks, platform variables, idempotence, and security validation.
3. **`simple-nginx` role**: Migrate Nginx installation, service management, and static page ownership/content. Add role defaults only for settings that will be actively rendered.
4. **Dependency and integration validation**: Integrate the roles in a site playbook, test both supported OS families, verify repeat runs are unchanged, and resolve package/service differences.
5. **Hardening and operational handover**: Decide on TLS, firewalling, Redis restrictions, logging, monitoring, and persistence; document ownership and retire the Chef implementation after parallel validation.

### Assumptions

- The repository root represents the primary `simple-nginx` Chef cookbook, despite the absence of a directory named `simple-nginx`.
- `cookbooks/cache` is an individual local cookbook and must be represented as an individual Ansible role or equivalent component.
- The visible files are the complete relevant source; no Berksfile, Policyfile, lock file, tests, environments, data bags, templates, or hidden deployment wrappers are assumed.
- The external `nginx` dependency is declarative metadata only unless repository owners confirm otherwise.
- The migration target is behavioral equivalence with the visible recipes, not an expansion into a complete production web/cache platform.
- The Nginx port remains 80 unless requirements change; HTTPS and firewall behavior are currently unspecified.
- The declared Nginx attributes are intended future/configuration inputs, although the visible recipe does not consume them.
- Redis is intended to run as a local cache service, but its required bind address, authentication, persistence, and client topology are unspecified.
- Ubuntu `>= 18.04` and CentOS `>= 7.0` are source-declared compatibility claims, not evidence of current production testing.
- No secrets are present in the reviewed files; secret requirements may exist outside this repository.
- No virtualization or cloud platform should be assumed.
- Team coordination should include Chef owners, platform/Ansible maintainers, security reviewers for Redis and network exposure, and operations owners responsible for cutover and rollback.
