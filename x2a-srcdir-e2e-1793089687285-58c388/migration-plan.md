# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef cookbook set containing one primary Nginx cookbook and one local cache dependency. The migration is low in volume but has a meaningful dependency and platform-normalization decision: the root cookbook declares both a local `cache` cookbook and an external `nginx` cookbook, while its default recipe directly installs and starts Nginx. The cache cookbook directly installs and starts Redis. A focused implementation should take approximately 3–5 engineering days, including playbook design, Ubuntu/CentOS validation, dependency replacement, security review, and handover; allow approximately 1–2 additional weeks if production acceptance, CI integration, and multiple operating-system versions are required.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Primary Chef cookbook that installs the Nginx package, enables and starts the Nginx service, and writes a static welcome page at `/var/www/html/index.html`.
    - Path: `.`
    - Technology: Chef
    - Key Features: Nginx package installation, service enablement and startup, root-owned static web content, default Nginx attributes for port, worker processes, and user.

- **cache**:
    - Description: Local Chef dependency that installs Redis using the platform package manager and enables and starts the `redis-server` service.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Redis package installation and service lifecycle management; no templates, credentials, or configurable attributes were identified in the reviewed entrypoint and metadata.

**CRITICAL PATH VERIFICATION:**
The two module paths above were present in the supplied repository tree. The root cookbook's primary entrypoint is `recipes/default.rb`; the local dependency's primary entrypoint is `cookbooks/cache/recipes/default.rb`.

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata for `simple-nginx`, including Chef version compatibility, supported operating systems, version, and declared dependencies. Migrate these constraints into Ansible documentation, role metadata, and CI test matrices.
- `recipes/default.rb`: Root Chef implementation to replace with an Ansible role or playbook for Nginx installation, service state, and index-page deployment.
- `attributes/default.rb`: Chef defaults for Nginx port, user, and worker process count. Convert these to documented role defaults or variables; note that the reviewed recipe does not currently consume them directly.
- `cookbooks/cache/metadata.rb`: Metadata for the local Redis cookbook, including supported platforms and Chef version.
- `cookbooks/cache/recipes/default.rb`: Redis installation and service implementation to replace with an Ansible role or an explicitly documented prerequisite task set.
- `README.md`: Describes the repository as a metadata-only dependency-strategy test and identifies `cache` as local and `nginx` as external. Update it to describe the new Ansible roles, inventories, variables, and validation procedure.

## Target Details

- **Operating System**: The source explicitly supports Ubuntu `>= 18.04` and CentOS `>= 7.0`. The implementation uses Debian-style package/service names (`redis-server`, `www-data`) and `/var/www/html`, so Ubuntu is the clearest current target. Ansible should either preserve Ubuntu support and add a Red Hat-family mapping, or formally constrain the first migration release. For a new target baseline where the source is ambiguous, use the requested enterprise default of Red Hat Enterprise Linux 9, but validate package names (`redis` versus `redis-server`), service names, web-root paths, and Nginx user ownership before claiming RHEL support.
- **Virtual Machine Technology**: Not specified. No VM, image, cloud-init, or hypervisor configuration was reviewed or present in the supplied tree.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, metadata-service, or cloud SDK configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Chef >= 16.0**: Remove Chef client execution and express convergence through Ansible playbooks/roles. Use `ansible-core` versions selected by the target automation platform and pin them in the project's dependency/CI process.
- **Local `cache` cookbook**: Replace with a dedicated Ansible `redis`/`cache` role or a clearly named task include. Preserve package installation and enabled/running service behavior, with OS-specific package and service variables.
- **External `nginx` cookbook**: The dependency is declared in root `metadata.rb`, but the repository contains no vendored implementation or lock/resolve file. Determine whether it supplied configuration behavior in the original Chef environment. In Ansible, use a maintained Nginx role or implement the required tasks locally; do not assume the dependency is unnecessary solely because the reviewed default recipe installs the package directly.
- **Ubuntu/CentOS package and service providers**: Replace Chef's provider abstraction with Ansible facts and variable maps. Test Nginx and Redis package names, service names, filesystem paths, and default users separately on Debian and Red Hat families.
- **Chef attributes**: Map `default['nginx']['port']`, `user`, and `worker_processes` to role defaults or inventory/group variables. Decide whether they should drive an Nginx configuration template, because the current default recipe does not use them.

### Security Considerations

- **Service exposure**: The source starts Nginx on port 80 but does not configure firewall rules, TLS, virtual hosts, access controls, or rate limiting. Define intended network exposure in Ansible and add firewall/TLS controls if this is production-facing.
- **Redis exposure**: The cache cookbook only starts Redis; no bind address, authentication, protected mode, TLS, or firewall policy is visible. Default Redis exposure must be verified and explicitly hardened, especially on multi-host networks.
- **File ownership and permissions**: Preserve root ownership and mode `0644` for the static page, but review whether the content should be generated from a managed template and whether the web-root ownership is correct on both OS families.
- **Configuration drift**: The current recipes manage package and service state but not Nginx or Redis configuration files. Ansible should define the intended configuration boundaries and use handlers to restart/reload services only when configuration changes.
- **Vault/secrets management**: No Chef encrypted data bags, Chef Vault references, hardcoded credentials, environment-variable secrets, private keys, or certificate references were visible in the reviewed files. Redis authentication and future TLS certificates would be new sensitive inputs; store them in Ansible Vault or an approved external secret manager, not in plaintext variables.
- **Supply-chain controls**: The external `nginx` dependency is unresolved in this repository. Pin and review any Ansible Galaxy role or collection, and use checksums/signature and dependency-locking practices appropriate to the organization.

### Technical Challenges

- **Unresolved external dependency semantics**: The `nginx` cookbook is declared but absent from the supplied tree, and the README says it is not fetchable without Berkshelf/Policy. Inspect the source deployment context before migration to determine whether it contributed configuration, repositories, or platform logic.
- **Cross-platform behavior**: Ubuntu and CentOS are declared, but the implementation uses names that may not be portable. Build a small matrix for Ubuntu and the selected RHEL baseline, with idempotence checks and service verification.
- **Unused Nginx attributes**: Port, user, and worker-process defaults exist but are not consumed by the reviewed recipe. Establish whether they are legacy metadata, intended inputs from another cookbook, or required production behavior before exposing them as Ansible variables.
- **Role boundary and ordering**: Nginx and Redis are separate concerns. Define whether Redis is a prerequisite for the web role, an independent cache role, or merely a dependency-test fixture. Coordinate inventory groups and play ordering rather than embedding all tasks in one playbook.
- **Configuration completeness**: The source provides only a static page and service lifecycle. Migration acceptance criteria must distinguish behavioral parity from desired hardening and production configuration, avoiding accidental assumptions about virtual hosts or application backends.
- **Testing and rollback**: Add syntax checks, linting, Molecule or equivalent disposable-instance tests, repeated-run idempotence tests, package/service assertions, and a rollback plan for package/configuration changes.

### Migration Order

1. **Inventory and dependency clarification**: Confirm the intended role of the absent external `nginx` cookbook, target OS baseline, Redis topology, and whether the attributes are required.
2. **`cache`**: Migrate the small, low-risk Redis package/service role first. Add platform mappings, service checks, and baseline Redis security controls.
3. **`simple-nginx`**: Implement the Nginx role for package installation, service enablement, static index deployment, and explicit variable handling. Validate port/user/worker-process expectations.
4. **Integration and hardening**: Compose the roles in an environment playbook, add firewall/TLS decisions, test Ubuntu and the selected Red Hat-family target, and remove Chef execution only after parallel validation.
5. **Operational handover**: Update README and runbooks, document inventory variables and secrets, train the operations team, and establish ownership for role dependency updates.

### Assumptions

- The supplied tree is complete; no Berksfile, Policyfile, Chef environment/role files, lock files, templates, or hidden deployment configuration were provided.
- The root directory represents the `simple-nginx` cookbook, while `cookbooks/cache` is a separate local cookbook because it has its own metadata and recipe entrypoint.
- `nginx` is an external Chef dependency, not a third module in this repository; its implementation and exact version are unknown.
- The reviewed recipes are the authoritative behavior for this migration. Any behavior supplied indirectly by Chef community cookbooks or node attributes remains to be verified.
- Port 80 is the intended HTTP endpoint, and the static index page is required behavior rather than test-only content; this must be confirmed with stakeholders.
- Redis is intended to run locally on the managed host and does not require a remote cluster, persistence policy, replication, or application-specific configuration unless discovered elsewhere.
- No secrets or certificates are currently required by the reviewed source, but production security requirements may introduce them.
- Ubuntu support is likely the most faithful initial target because of `www-data`, `redis-server`, and the Debian-style web root; CentOS/RHEL support requires explicit validation rather than filename-based assumptions.
- No cloud, VM, inventory, network, firewall, monitoring, backup, or CI platform is specified.
- The timeline estimate assumes a clean, small migration with stakeholder access; hidden dependencies, production hardening, or undocumented cookbook behavior may materially increase it.
