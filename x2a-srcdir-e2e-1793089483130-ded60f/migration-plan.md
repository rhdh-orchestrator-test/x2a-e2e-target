# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef codebase with exactly two independently identifiable cookbook modules: the root cookbook (`.`) and the nested local `cache` cookbook (`cookbooks/cache`). Their default recipes perform simple package, service, and static-file management. The migration is low complexity and should take approximately 3–5 working days for implementation and validation, plus 2–5 additional days if the undeclared behavior of the external `nginx` cookbook must be reconstructed. The primary risks are ambiguity around Chef dependency resolution, unused Nginx attributes, and the lack of tests, inventory, and environment configuration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning. The inventory below includes every directory in the supplied tree containing a Chef `recipes/default.rb` entrypoint.

### MODULE INVENTORY

- **simple-nginx (root cookbook)**:
    - Description: Primary Chef cookbook that installs Nginx, enables and starts the Nginx service, and creates a static welcome page at `/var/www/html/index.html`.
    - Path: `.`
    - Existing directory verification: Repository root `.` exists and contains `recipes/default.rb`, `metadata.rb`, `attributes/default.rb`, and `README.md`.
    - Primary entrypoint: `recipes/default.rb`
    - Technology: Chef
    - Key Features: Nginx package installation; service enablement and startup; root-owned `0644` static page; default attributes for port 80, `www-data`, and automatic worker processes.

- **cache**:
    - Description: Local Chef cookbook that installs Redis as a basic caching service and enables and starts it.
    - Path: `cookbooks/cache`
    - Existing directory verification: Directory `cookbooks/cache` exists and contains `recipes/default.rb` and `metadata.rb`.
    - Primary entrypoint: `cookbooks/cache/recipes/default.rb`
    - Technology: Chef
    - Key Features: `redis-server` package installation and Redis service enablement/startup; Ubuntu and CentOS support declarations.

**CRITICAL PATH VERIFICATION:**
Both required module paths are directly confirmed by the supplied repository tree and directory listings: `.` contains `recipes/default.rb`, and `cookbooks/cache` contains `recipes/default.rb`. They are separate cookbook entries and must not be merged. No Puppet `manifests/init.pp` files or PowerShell `.psd1` module manifests are present in the supplied tree, so no additional modules are identified.

### Infrastructure Files

- `metadata.rb`: Root `simple-nginx` cookbook metadata. It declares Chef `>= 16.0`, Ubuntu `>= 18.04`, CentOS `>= 7.0`, and dependencies on local `cache` and external `nginx`. Replace cookbook dependency resolution with Ansible roles, collections, and explicit playbook ordering.
- `recipes/default.rb`: Root cookbook implementation. Convert the package, service, and file resources to `ansible.builtin.package`, `ansible.builtin.service` or `ansible.builtin.systemd`, and `ansible.builtin.copy` tasks.
- `attributes/default.rb`: Root defaults for Nginx port, user, and worker processes. Convert these to role defaults or inventory/group variables only after confirming they are intended to affect managed Nginx configuration.
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and supported OS declarations. Represent this cookbook as a dedicated Redis/cache Ansible role.
- `cookbooks/cache/recipes/default.rb`: Redis package and service implementation. Convert it to idempotent package and service tasks.
- `README.md`: Documents the metadata-only dependency strategy and identifies `cache` as local and `nginx` as external. Update it with Ansible inventory, roles, execution, testing, and rollback instructions.

## Target Details

- **Operating System**: The Chef metadata explicitly supports Ubuntu `>= 18.04` and CentOS `>= 7.0`. The Ansible migration should target currently supported Ubuntu LTS and/or RHEL-compatible releases rather than automatically preserving end-of-life versions. Validate package and service names, particularly Redis naming, per distribution.
- **Virtual Machine Technology**: Not specified. No VM tooling, cloud-init, provider configuration, or virtualization-specific package was found.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, cloud metadata endpoint, or cloud CLI configuration was found.

## Migration Approach

Create an Ansible project with a playbook that applies the Redis/cache role before the Nginx role:

1. `roles/cache` or `roles/redis`: install the correct Redis package and enable/start the correct service.
2. `roles/simple_nginx`: install Nginx, enable/start it, and deploy the welcome page with `root:root` ownership and mode `0644`.
3. Group/host variables: carry forward port, user, and worker-process values only if an approved Nginx configuration task consumes them.
4. Verification: run idempotence checks, service/package assertions, an HTTP check for the welcome page, and a Redis health check.

The root recipe does not explicitly invoke a `cache` recipe, although root metadata declares `cache` as a dependency. Confirm the effective Chef run list and dependency behavior before defining the Ansible playbook. The external `nginx` dependency has no version or source in this repository; determine whether it supplied configuration beyond the root recipe.

### Key Dependencies to Address

- **Chef `>= 16.0`**: Replace the Chef runtime with a supported Ansible Core version and document controller/target compatibility.
- **Local `cache` cookbook**: Replace with a dedicated Redis/cache role and explicit playbook ordering.
- **External `nginx` cookbook**: No version or source is declared. Use native Ansible Nginx tasks or a vetted role after effective Chef behavior is confirmed.
- **Ubuntu `>= 18.04` and CentOS `>= 7.0`**: Test against approved supported releases and use OS-family variables for package/service differences.
- **OS package repositories**: The source assumes Nginx and Redis are available from configured repositories. Confirm repository, proxy, version-pinning, and update policies.

### Security Considerations

- **Visible secrets**: No passwords, tokens, private keys, encrypted data bags, Chef Vault references, certificates, or secret environment variables appear in the reviewed files. Confirm that deployment systems and external dependencies contain no additional secrets.
- **File permissions**: Preserve `/var/www/html/index.html` as owned by `root:root` with mode `0644`; confirm whether the file may overwrite existing application content.
- **Service exposure**: The source starts Nginx and Redis but does not configure firewall rules, Redis bind addresses, authentication, TLS, or network ACLs. Decide explicitly whether Redis is local-only and how Nginx port 80 is exposed.
- **Unused configuration attributes**: `nginx.port`, `nginx.user`, and `nginx.worker_processes` are declared but not referenced by the reviewed root recipe. Do not assume they currently configure Nginx; validate external cookbook behavior before implementing them.
- **Ansible secret handling**: If Redis authentication, TLS material, upstream credentials, or private keys are added, store them in Ansible Vault or an approved external secret manager, never plaintext role defaults.
- **Privilege and supply chain**: Use controlled `become`, pin or constrain package/collection versions where necessary, and review third-party roles and collections before installation.

### Technical Challenges

- **External dependency ambiguity**: The `nginx` dependency lacks a source and version. Compare a real Chef-converged host with the repository behavior before claiming parity.
- **Dependency execution ambiguity**: Root metadata declares `cache`, but the reviewed root recipe does not explicitly include its recipe. Confirm whether Chef metadata dependency loading is part of the intended run.
- **Distribution differences**: Ubuntu and CentOS package/service conventions differ, and the declared minimum versions are obsolete. Use OS-specific variables and test on supported images.
- **Unused attributes**: Determine whether Nginx configuration was supplied by the external cookbook or is simply future intent. Obtain owner approval before adding behavior not observed in the recipe.
- **Missing Redis hardening**: Redis is started with no visible access controls. Establish security requirements before production rollout.
- **Limited operational scaffolding**: No inventory, environments, tests, CI pipeline, or rollback procedure is present. Add Ansible linting, Molecule or equivalent integration tests, staged inventory, ownership, and rollback documentation.

### Migration Order

1. Confirm the effective Chef run list, external `nginx` behavior, supported OS targets, repository policy, and intended meaning of the unused attributes.
2. Migrate and harden the `cache` cookbook as a Redis/cache Ansible role.
3. Migrate the root `simple-nginx` cookbook as an Nginx role, including package, service, and static page behavior.
4. Integrate both roles in dependency order and validate Redis health, Nginx service state, HTTP response, file ownership, and repeat-run idempotence.
5. Perform security and owner acceptance review, deploy through a staged inventory, document Chef rollback, and retire Chef only after parity is accepted.

### Assumptions

- The supplied repository tree is complete for this assessment.
- The root directory `.` is an independently identifiable Chef cookbook because it contains `recipes/default.rb` and root `metadata.rb`.
- `cookbooks/cache` is a second, separate cookbook because it independently contains `recipes/default.rb` and `metadata.rb`.
- No other directory contains a Puppet `manifests/init.pp`, Chef `recipes/default.rb`, or PowerShell `.psd1` manifest.
- No Berksfile, Policyfile, lockfile, tests, environments, wrapper cookbook, or external cookbook source is present.
- The external `nginx` cookbook may have supplied behavior outside this repository, but its version and implementation are unknown.
- Supported modern OS releases will be used unless legacy Ubuntu/CentOS targets are explicitly required.
- Package repositories provide Nginx and Redis, or repository setup will be separately added and approved.
- No secrets, TLS, firewall, monitoring, backup, clustering, or application upstream behavior is in scope based on the reviewed files.
- Ansible inventory source, controller platform, privilege policy, CI/CD system, and target topology remain to be selected by the operations team.
- The timeline assumes a clean target environment and owner availability; undocumented external cookbook behavior may extend it.
