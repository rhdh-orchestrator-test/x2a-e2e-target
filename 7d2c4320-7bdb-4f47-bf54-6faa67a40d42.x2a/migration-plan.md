# MIGRATION FROM CHEF INFRA SERVER / CHEF AUTOMATE SUPPORT SCRIPTS TO ANSIBLE

This repository is a small Chef-oriented example repository rather than a collection of Chef cookbooks. The deploy scripts provision Chef Automate or Chef Infra Server, while the `chef-and-ansible` directory already contains Ansible playbooks and InSpec verification tests for an Apache HTTPS example. No `recipes/default.rb`, `metadata.rb`, `Berksfile`, `Policyfile.rb`, or other cookbook entrypoints were present in the supplied tree, so there are no Chef cookbooks to migrate individually. The practical migration is to preserve or retire the example web configuration and replace the Chef platform bootstrap scripts with a secure, idempotent Ansible control-plane or host-provisioning workflow. The scope is small and should take approximately 1–2 weeks for implementation, testing, security remediation, and documentation, assuming no omitted production cookbooks or external deployment requirements.

## Module Migration Plan

This repository contains a mixed Chef-adjacent and Ansible example, with no discoverable Chef cookbook modules:

### MODULE INVENTORY

- **apache-https-example**:
    - Description: An Ansible playbook example that installs a pinned Apache 2.4 package on Ubuntu, generates a self-signed TLS key/CSR/certificate, creates a Hello World HTTPS virtual host and content, enables SSL, and restarts Apache.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible
    - Key Features: Ubuntu APT installation, Apache virtual-host configuration, OpenSSL key/CSR/self-signed certificate generation, HTTPS listener, sample web content, InSpec verification

- **apache-ssl-hardening-example**:
    - Description: An Ansible playbook that changes Apache's SSL protocol configuration to permit TLS 1.2 and notifies Apache and SSH service handlers.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible
    - Key Features: SSL protocol replacement in `/etc/apache2/mods-available/ssl.conf`, service restart handlers

- **Chef Automate and Infra Server bootstrap**:
    - Description: Shell-based bootstrap for deploying Chef Automate together with Chef Infra Server, then creating a Chef Server user and organization.
    - Path: `setup-automate/deploy-automate.sh`
    - Technology: Bash with Chef Automate/Infra Server CLI
    - Key Features: Host kernel tuning, downloaded Chef Automate CLI, Automate and Infra Server deployment, user and organization creation, generated PEM credentials

- **Chef Infra Server bootstrap**:
    - Description: Shell-based bootstrap for deploying Chef Infra Server without Automate, then creating a Chef Server user and organization.
    - Path: `setup-automate/deploy-chef-server.sh`
    - Technology: Bash with Chef Infra Server CLI
    - Key Features: Hostname and kernel tuning, downloaded Chef Automate CLI, Infra Server deployment, user and organization creation, generated PEM credentials

**CRITICAL PATH VERIFICATION:**
The paths above were present in the supplied repository tree and were read during analysis. No cookbook path was inferred or invented. The repository tree contains no Chef cookbook directory with `recipes/`, `metadata.rb`, or `manifests/`; the only Ruby files are InSpec tests.

### Infrastructure Files

- `README.md`: Repository-level description of Chef examples; migration consideration is to update it to describe the Ansible target and supported execution paths.
- `chef-and-ansible/README.md`: Describes using Chef InSpec with Ansible for continuous compliance; retain or revise as the migration's testing and compliance rationale.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, the Ansible playbook provisioner, Ubuntu 20.04, and InSpec verification. Convert to the chosen Ansible CI/test framework or retain temporarily as an integration harness.
- `chef-and-ansible/website_https.yml`: Primary Apache HTTPS example and likely source for an Ansible role/playbook.
- `chef-and-ansible/poodle_fix.yml`: SSL hardening playbook; consolidate its behavior into the Apache role and replace broad text replacement with a managed configuration/template where practical.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec checks for port 443, HTTPS response, disabled SSLv3, and enabled TLS 1.2. Keep as acceptance coverage during migration, or translate equivalent checks to Ansible Molecule/Testinfra where organizational standards require it.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance check for disabled SSH root login, with an alternate condition that treats an absent OpenSSH server as acceptable. Its path/name do not match the suite shown in `kitchen.yml`, so test wiring requires clarification.
- `setup-automate/deploy-automate.sh`: Chef platform deployment bootstrap; replace shell execution with an idempotent Ansible playbook only if Chef platform deployment remains in scope.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server-only deployment bootstrap; same migration decision as above.

### Target Details

- **Operating System**: Ubuntu 20.04 is explicitly specified in `chef-and-ansible/kitchen.yml`. The web example uses `apt`, `/etc/apache2`, and Debian/Ubuntu service naming. The Chef deployment scripts do not specify an OS and may have separate Chef Automate support requirements; validate the supported target OS before automating them.
- **Virtual Machine Technology**: Vagrant is specified as the Test Kitchen driver. The deployment scripts describe on-premises or cloud VMs but do not identify a production hypervisor.
- **Cloud Platform**: Not specified. The scripts are intended for either on-premises or cloud VMs and contain no provider SDK, metadata endpoint, or cloud resource definitions.

## Migration Approach

### Key Dependencies to Address

- **Ansible**: Standardize on a supported Ansible version and use fully qualified collection names. Refactor the existing playbooks into an `apache_https` role with defaults, handlers, templates, and environment-specific variables.
- **Ubuntu APT and Apache 2.4.41-4ubuntu3.10**: The web playbook pins this package version. Confirm repository availability and security support; use a tested package policy or a controlled repository rather than allowing an unavailable pin to block deployment.
- **`community.crypto` Ansible collection**: Replace legacy/unqualified `openssl_privatekey`, `openssl_csr`, and `openssl_certificate` usage with supported collection modules and explicit certificate ownership, permissions, and renewal behavior.
- **Apache enablement commands (`a2ensite`, `a2dissite`, `a2enmod`)**: Replace imperative `command` tasks with idempotent Ansible modules or carefully guarded commands, followed by configuration validation and handler-driven reloads.
- **Chef Automate CLI and Chef Infra Server**: These are external Chef platform dependencies, downloaded from `packages.chef.io` at runtime. Decide whether they are out of scope after migration; if retained, pin a supported release, verify downloads, and use vendor-supported installation procedures rather than an unpinned “latest” binary.
- **Vagrant, Test Kitchen, and InSpec**: Preserve for transitional acceptance testing or replace with Molecule and an appropriate verifier. Ensure the test image is still available and matches the target Ubuntu baseline.

### Security Considerations

- **Hardcoded credentials**: Both deployment scripts visibly contain `userpassword='password'`, along with user and email identity values. Remove all passwords from source immediately; use Ansible Vault, an enterprise secret manager, or a one-time secure input. Rotate any credentials that may have been used.
- **Generated Chef PEM credentials**: The scripts create user and organization validator PEM files in the working directory. Treat these as private keys, restrict permissions, avoid source control and logs, establish rotation/revocation, and store them in an approved secret store if Chef remains.
- **TLS private key and certificate**: The web playbook generates `/etc/apache2/certs/apache.key`, CSR, and self-signed certificate. Set explicit restrictive ownership/modes, protect the private key, and replace self-signed certificates with an approved CA or ACME workflow for real environments. Define renewal and replacement behavior.
- **TLS protocol policy**: The intended policy disables SSLv3 and enables TLS 1.2. Validate the resulting Apache configuration against current organizational policy, including whether TLS 1.3 should be enabled and whether weak ciphers are excluded. Do not restart SSH merely as a side effect of an Apache SSL change unless a separate SSH change requires it.
- **SSH hardening**: The InSpec profile checks that root SSH login is not allowed, but neither supplied web playbook actually manages `PermitRootLogin`. Add a dedicated, tested SSH hardening role with a rollback path and console/out-of-band access before applying it broadly.
- **Unsafe download and shell practices**: The deployment scripts pipe a remotely downloaded “latest” archive through `gunzip` and execute it, with no checksum/signature verification. Pin versions, verify provenance and checksums, download to a controlled location, and restrict execution privileges.
- **File and directory modes**: The certificate directory is created with mode `0640`, which is not a conventional directory mode because directory traversal requires execute permission. Define intended access explicitly and use least-privilege modes for directories, certificates, keys, and web content.
- **Secrets management by module**: The Apache example has certificate private-key material rather than user credentials; the two Chef bootstrap scripts have plaintext administrative credentials and generate PEM keys. No encrypted data bags, Chef Vault references, environment-variable secrets, or external secret manager integration were visible in the reviewed files.

### Technical Challenges

- **No actual Chef cookbooks are present**: There is no cookbook metadata or recipe inventory to translate. Confirm that this is the complete repository and obtain any external Chef cookbook repositories before declaring the migration complete.
- **Mixed technology ownership**: The web configuration is already Ansible, the tests are InSpec Ruby, and platform provisioning is Bash/Chef CLI. Establish one source of truth and define whether the objective is Ansible host configuration only or replacement of Chef Automate/Infra Server itself.
- **Idempotence and configuration drift**: Imperative `a2ensite`, `a2dissite`, and `a2enmod` commands, plus text replacement of `ssl.conf`, need idempotence, check-mode behavior, and validation. Use templates/modules and notify reloads only when content changes.
- **Certificate lifecycle**: Self-signed certificate creation is suitable for a demo but not production. Select CA/ACME integration, hostname/SAN policy, renewal timing, and safe reload behavior.
- **Version and platform compatibility**: Ubuntu 20.04 and the pinned Apache package are aging baselines. Test the intended supported OS and package versions, while separately validating Chef Automate's vendor support matrix if it remains.
- **Test coverage and wiring**: `kitchen.yml` references `website_https_verify.rb`, while `ssh_profile.rb` is not shown as an active suite test. Expand tests to verify Apache config syntax, file modes, certificate validity, service state, and SSH policy; add negative and rollback tests.
- **Chef platform replacement scope**: Ansible does not directly replace Chef Automate's reporting, compliance, server organizations, or Chef client ecosystem. If those capabilities are required, plan a separate platform decision (for example, Ansible Automation Platform/AWX and an approved secrets/compliance stack).

### Migration Order

1. **Repository and scope confirmation**: Inventory any external cookbooks, Chef Server dependencies, target OS requirements, and ownership. Freeze the insecure bootstrap scripts and rotate exposed credentials.
2. **Apache HTTPS role**: Convert `website_https.yml` into a tested, reusable Ansible role. Parameterize hostname, package version, document root, virtual host, certificate source, and TLS policy.
3. **SSL hardening and SSH policy**: Merge `poodle_fix.yml` into the role or a separate hardening role, eliminate unnecessary SSH restarts, and implement the missing `PermitRootLogin` control with controlled rollout.
4. **Acceptance and CI migration**: Run the existing InSpec tests during transition, then add Molecule/Testinfra or the team's standard Ansible validation. Test Ubuntu 20.04 and the final supported OS.
5. **Chef bootstrap decision and replacement**: If Chef Automate/Infra Server is no longer needed, retire both shell scripts and document the replacement control-plane architecture. If it remains, create a separate, version-pinned Ansible bootstrap with secure secret handling and explicit vendor compatibility checks.
6. **Documentation and handover**: Update READMEs, operational runbooks, ownership, rollback procedures, inventory/group variables, secret-management instructions, and CI/CD promotion gates.

### Assumptions

- The supplied tree is complete; no external Chef cookbooks, Berksfiles, Policyfiles, Chef roles, environments, or production inventories were omitted.
- “Migration to Ansible” primarily concerns the examples and bootstrap scripts, not a full migration of an existing production Chef estate.
- The intended web target is Ubuntu 20.04 because it is the only explicit platform declaration.
- Vagrant is used for local integration testing, not necessarily production virtualization.
- The Apache site and self-signed certificate are demonstration assets; production certificate authority requirements are not provided.
- The Chef Automate and Chef Infra Server scripts may be examples rather than required target services; scope must be confirmed with the platform owner.
- The Chef CLI download URL's `latest` behavior, archive format, checksums, and supported operating systems are not pinned or documented.
- The Apache package pin may no longer be available in configured repositories and should not be treated as a guaranteed target version.
- The existing InSpec checks are intended as acceptance tests, but test-suite wiring for `ssh_profile.rb` is unclear.
- No inventory, variables, vault configuration, CI pipeline, cloud account, DNS, CA, monitoring, backup, or rollback configuration is present.
- No runtime execution results were provided; service behavior, package availability, certificate validity, and Chef platform compatibility require validation in a controlled environment.
- A 1–2 week estimate applies to this small visible scope with an available Ansible owner; production platform replacement or discovery of external cookbooks would materially increase the timeline.
