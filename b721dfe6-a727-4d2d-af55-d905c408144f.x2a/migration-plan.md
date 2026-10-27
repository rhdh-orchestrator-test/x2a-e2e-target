# MIGRATION FROM CHEF TO ANSIBLE

This repository is a Chef cookbook set containing two independently identifiable cookbook modules: the root cookbook at `.` and the local `cache` cookbook at `cookbooks/cache`. The migration is low-to-moderate complexity because the recipes only manage packages, services, and one static file. A basic conversion and validation should take approximately 2–4 working days; cross-platform testing, security hardening, CI, and staged rollout may require an additional 1–2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that require separate Ansible migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Both entries below correspond to directories present in the repository tree and each has a separate `recipes/default.rb` entrypoint.

- **simple-nginx**:
    - Description: Root Chef cookbook that installs Nginx, enables and starts its service, and creates a static HTML landing page at `/var/www/html/index.html`.
    - Path: `.`
    - Technology: Chef
    - Primary entrypoint: `recipes/default.rb`
    - Key Features: Nginx package installation, service enablement/start, root-owned static content with mode `0644`, and default Nginx attributes for port `80`, user `www-data`, and automatic worker processes.
    - Ansible target: A dedicated `simple_nginx` role with package, service, and `copy`/template tasks plus role defaults for any attributes confirmed to be required.

- **cache**:
    - Description: Local Chef cookbook dependency that installs Redis and enables and starts the `redis-server` service.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Primary entrypoint: `cookbooks/cache/recipes/default.rb`
    - Key Features: Redis package installation and service lifecycle management; no templates, secrets, or custom configuration were identified in the reviewed files.
    - Ansible target: A separate `cache` or `redis` role with OS-specific package and service variables.

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata for `simple-nginx`, version `1.0.0`, Chef `>= 16.0`, Ubuntu `>= 18.04` and CentOS `>= 7.0` support, and dependencies on local `cache` plus external `nginx`. Convert dependency intent into Ansible role/collection documentation and pinned requirements.
- `recipes/default.rb`: Root cookbook implementation. Translate its package, service, and file resources to idempotent Ansible tasks.
- `attributes/default.rb`: Defines `nginx` defaults: port `80`, user `www-data`, and worker processes `auto`. Convert to role defaults only after confirming their intended use because the reviewed recipe does not consume them.
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata, version `1.0.0`, Chef `>= 16.0`, and Ubuntu/CentOS support information.
- `cookbooks/cache/recipes/default.rb`: Redis package and service implementation to convert into the Redis/cache role.
- `README.md`: Explains that this is a metadata-only dependency-strategy test, identifies `cache` as local and `nginx` as external, and should be retained as migration documentation.
- No `Berksfile`, `Policyfile.rb`, or dependency lock file is present in the supplied tree.

## Target Details

- **Operating System**: Source metadata declares Ubuntu `>= 18.04` and CentOS `>= 7.0`. Ubuntu is the clearest fit because the recipe uses the `redis-server` package/service name and `www-data` user. CentOS/RHEL compatibility requires explicit validation and likely platform-specific names. Use RHEL 9 or a compatible current distribution as the default Red Hat target rather than assuming legacy CentOS 7.
- **Virtual Machine Technology**: Not specified; no VM, image, cloud-init, or virtualization configuration is present.
- **Cloud Platform**: Not specified; no cloud SDK, metadata endpoint, or provider integration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef `>= 16.0`**: Replace the Chef runtime with a documented Ansible Core/Python support matrix and CI checks.
- **Local `cache` cookbook**: Migrate independently as a Redis/cache role, then compose it from a site playbook where Redis is intended to run.
- **External `nginx` cookbook**: The root `metadata.rb` declares `nginx`, but its source and version are absent. Confirm whether it provided behavior beyond the root recipe. Replace only required behavior with native Ansible tasks or a reviewed, pinned Galaxy role.
- **OS package repositories**: Chef relies on platform defaults. Define package names, service names, users, and repository assumptions per OS, particularly for Redis on RHEL-family systems.
- **Dependency locking**: Since no Berkshelf or Policyfile lock is present, create and pin `collections/requirements.yml` and any external role requirements used by the Ansible implementation.

### Security Considerations

- **Redis exposure**: The source starts Redis but does not configure bind addresses, authentication, TLS, persistence, or firewall rules. Default the service to restricted access and obtain an explicit network/security requirement before exposing it.
- **Nginx exposure**: The source starts Nginx without TLS, firewall rules, security headers, rate limits, or virtual-host configuration. Treat these as separate hardening requirements rather than assumed migrated behavior.
- **File permissions**: Preserve the index file as owned by `root:root` with mode `0644`; avoid broad document-root permissions.
- **Privilege escalation**: Package and service operations require Ansible `become: true`. Keep escalation scoped to required tasks.
- **Secrets and credentials**: No encrypted data bags, Chef Vault usage, plaintext passwords, certificates, private keys, or environment-variable secrets were visible in the reviewed files. Any future credentials must use Ansible Vault or an approved external secrets manager.
- **Supply chain**: The unresolved external `nginx` cookbook is a dependency and provenance risk. Pin and review any Ansible collection or role that replaces it.

### Technical Challenges

- **Unresolved external dependency**: `nginx` is declared but unavailable in the repository, while the root recipe already installs Nginx. Confirm whether the dependency is redundant or contains required configuration.
- **Attributes not used by the recipe**: Port, user, and worker-process attributes are declared but no Nginx configuration is rendered. Do not claim these settings are active until confirmed and tested.
- **Cross-platform behavior**: Ubuntu and CentOS are declared, but Redis package/service names and Nginx users may differ. Add OS-specific variables and integration tests.
- **Chef-to-Ansible idempotence**: Map Chef package/service/file resources to Ansible modules and verify a second playbook run reports no changes.
- **Deployment topology**: The source does not say whether Redis and Nginx share hosts. Model separate `webservers` and `cache_servers` inventory groups if required.
- **Limited implementation scope**: There are no tests, templates, firewall rules, TLS files, or service overrides. Preserve the observed behavior and record hardening as follow-on work rather than inventing configuration.

### Migration Order

1. Confirm supported target OS versions, host topology, acceptance criteria, and the purpose of the external `nginx` dependency.
2. Migrate `cache` at `cookbooks/cache` into a tested Redis role with platform-specific package/service variables and safe default exposure.
3. Migrate `simple-nginx` at `.` into an Nginx role covering package installation, service state, and static index deployment.
4. Create the composing playbook, inventory groups, role defaults, dependency requirements, and documentation.
5. Run linting, syntax checks, idempotence tests, Ubuntu and RHEL-family integration tests, security review, and staged rollout with rollback procedures.

### Assumptions

- The root directory `.` is a Chef cookbook whose primary entrypoint is `recipes/default.rb`.
- `cookbooks/cache` is a second, separate Chef cookbook whose primary entrypoint is `cookbooks/cache/recipes/default.rb`.
- `metadata.rb` files are the available dependency and platform authorities; no Berksfile, Policyfile, or lock file is present.
- The external `nginx` cookbook is not locally available, and its version and behavior are unknown.
- The root recipe represents the currently implemented Nginx behavior; the attributes may be illustrative or intended for future configuration.
- Redis is intended to run as a managed local service, but bind address, authentication, persistence, and firewall requirements are unspecified.
- The desired target cloud, VM platform, inventory, CI system, secrets backend, and production topology are unspecified.
- CentOS 7 is declared by the source but is legacy; stakeholders must confirm whether RHEL 9, Rocky, Alma, Ubuntu, or another supported platform is required.
- The timeline assumes no hidden behavior exists in the unavailable external `nginx` cookbook and that migration acceptance is limited to the reviewed package, service, and static-file behavior.
- Assign separate owners for role conversion, platform testing, security review, dependency management, and rollout coordination.
