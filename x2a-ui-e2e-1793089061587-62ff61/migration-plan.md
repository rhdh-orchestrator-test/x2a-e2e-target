# MIGRATION FROM ANSIBLE (WITH CHEF INFRASTRUCTURE SUPPORT SCRIPTS) TO ANSIBLE

The repository is primarily an existing Ansible example rather than a Chef cookbook or Puppet control repository. Its main workload consists of two Ansible playbooks that configure Apache HTTPS and TLS settings on Ubuntu 20.04, with Chef InSpec tests used for verification. Separate Bash scripts bootstrap Chef Infra Server and Chef Automate; these are infrastructure/bootstrap utilities, not Ansible modules. The practical migration scope is therefore a short Ansible consolidation and hardening effort, plus an explicit decision about whether the Chef server/Automate bootstrap is to be retained, replaced, or removed.

For the two application playbooks, an initial conversion/refactoring can be completed in approximately 1–2 weeks by one engineer. Production hardening, certificate/secret integration, CI validation, and any replacement of Chef Infra Server/Automate should be estimated separately at approximately 2–6 additional weeks depending on the target platform and operational requirements.

## Module Migration Plan

This repository contains Ansible playbooks and InSpec verification content that need individual migration planning. No Puppet modules, Chef cookbooks, PowerShell modules, or Salt states were identified.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only paths present in the supplied repository tree are listed below.

- **website_https**:
    - Description: Ansible playbook that installs a pinned Apache 2.4 package on Ubuntu, installs TLS-related utilities, creates a self-signed Apache certificate/key/CSR, configures an HTTPS virtual host for a Hello World site, disables the default site, enables the custom site and SSL module, and restarts services.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible
    - Key Features: Ubuntu `apt` package management, Apache HTTPS virtual host, generated OpenSSL material, content deployment, `a2ensite`, `a2dissite`, and `a2enmod` commands, service handlers.

- **poodle_fix**:
    - Description: Ansible playbook intended to mitigate the POODLE-era TLS risk by replacing the Apache SSL protocol setting with TLS 1.2 only and restarting Apache and SSH.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible
    - Key Features: Regex replacement of `/etc/apache2/mods-available/ssl.conf`, TLS protocol restriction, privileged execution, service notifications.

### Infrastructure Files

- `README.md`: Root repository description identifying the repository as Chef-related examples. It does not define a deployable module or target inventory.
- `chef-and-ansible/README.md`: Describes the examples as Chef InSpec compliance verification used alongside Ansible.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, Ubuntu 20.04, the Ansible provisioner, and InSpec verification. It is the principal test/lifecycle definition and should be replaced or retained as a transitional validation harness.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec control checking that SSH root login is disabled, with an alternate package assertion. It contains RHEL-oriented compliance metadata despite the Kitchen platform being Ubuntu.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec checks for port 443, HTTPS response/content, SSLv3 disabled, and TLS 1.2 enabled.
- `setup-automate/deploy-automate.sh`: Bash bootstrap for Chef Automate plus Chef Infra Server. It configures host/kernel settings, downloads the latest Chef Automate CLI, deploys products, and creates a Chef user and organization.
- `setup-automate/deploy-chef-server.sh`: Bash bootstrap for Chef Infra Server only, including host/kernel tuning, CLI download, user creation, and organization creation.

### Target Details

- **Operating System**: The explicit test target is Ubuntu 20.04 (`chef-and-ansible/kitchen.yml`). The playbooks use `apt`, Debian/Ubuntu Apache paths, and the `apache2`/`sshd` service names, so Ubuntu/Debian is the evidenced target family. The RHEL 8 references in the InSpec SSH control are compliance-control metadata, not evidence that the playbooks support RHEL. Confirm whether Ubuntu 20.04 remains supported or whether the target should be upgraded to a current Ubuntu LTS.
- **Virtual Machine Technology**: Vagrant is specified by Kitchen. The underlying provider is not stated.
- **Cloud Platform**: Not specified. The Chef bootstrap comments say on-premises or cloud VM, but no provider-specific resources or SDKs are present.

## Migration Approach

### Key Dependencies to Address

- **Ansible runtime and collections**: Pin a supported `ansible-core` version and explicitly declare required collections. Replace legacy/unqualified modules such as `apt`, `file`, and `copy` with fully qualified names where appropriate.
- **OpenSSL Ansible modules**: `openssl_privatekey`, `openssl_csr`, and `openssl_certificate` require the relevant Ansible collection/runtime support. Validate module behavior and idempotence, and use `community.crypto` explicitly if required by the selected Ansible version.
- **Apache and Ubuntu packages**: Preserve or deliberately revise the pinned `apache2=2.4.41-4ubuntu3.10` dependency. A repository/package mirror and compatibility policy are needed because the exact package may no longer be available.
- **Vagrant and Test Kitchen**: Decide whether Kitchen remains a transitional test runner or is replaced by Molecule, Ansible-native CI, or an image-based integration test. Keep InSpec controls if they remain the organization’s compliance standard.
- **Chef Infra Server/Automate**: The shell scripts download the current Chef Automate CLI and invoke Chef server commands. If Chef is being retired, replace these functions with Ansible Automation Platform/AWX, a chosen inventory and secrets platform, and separate observability/compliance tooling. If Chef remains, manage it as an external platform dependency rather than embedding credentials in scripts.
- **External certificate authority**: Self-signed certificates are suitable only for demonstrations or isolated test systems. Production Ansible should consume certificates from an approved CA, ACME workflow, or secrets/certificate manager.

### Security Considerations

- **Hardcoded Chef credentials**: Both bootstrap scripts visibly contain a plaintext user password (`password`), username, email, organization data, and a hostname. Remove these values from source, rotate any exposed credentials, and supply them through Ansible Vault, an external secret manager, or protected CI variables.
- **Generated private key**: `website_https.yml` creates `/etc/apache2/certs/apache.key`. Protect the directory and key with restrictive ownership/mode, avoid committing generated artifacts, and define backup/rotation behavior. The current directory mode `0640` is potentially problematic for directory traversal and does not specify owner/group.
- **Self-signed TLS**: The playbook generates a self-signed certificate with common name `myhost`. Replace this for real deployments with SAN-aware certificates and validated trust chains. Ensure private keys are not exposed in task output or logs.
- **TLS policy**: The POODLE playbook disables older protocols by writing `TLSv1.2` only, while the InSpec test checks SSLv3 and TLS 1.2. Confirm the desired TLS 1.2/1.3 policy and cipher suite policy rather than relying on a single protocol replacement. Use a managed Apache configuration/template and validate syntax before restarting.
- **Privileged execution**: Both playbooks use `remote_user: root` and `become: yes`. Prefer a controlled automation account with narrowly scoped privilege escalation, inventory-level SSH settings, and auditable access.
- **Unsafe shell/download behavior**: The bootstrap scripts pipe a remote “latest” download into `gunzip` and execute it, with no checksum or signature verification. Pin a release, verify checksum/signature, use a trusted artifact repository, and run installation in a controlled process.
- **Service disruption**: The TLS playbook restarts `sshd` as well as Apache even though its changes concern Apache. Validate SSH configuration before any SSH restart and avoid restarting unrelated services.
- **Credential patterns by module**: `website_https` contains certificate/key paths and generates private material but no user password; `poodle_fix` changes security-sensitive TLS configuration but contains no visible secret; the Chef bootstrap scripts contain plaintext account credentials and generate PEM key files. Treat generated PEM files as sensitive.

### Technical Challenges

- **Existing playbooks are not reusable roles**: Both playbooks are host-specific (`myhost`), use inline configuration/content, and assume root access. Refactor into roles such as `apache_https` and `tls_policy`, with variables for site name, document root, ports, package version, certificate source, and supported protocols.
- **Idempotence and command modules**: `a2dissite`, `a2ensite`, and `a2enmod` are invoked through `command`. Replace with idempotent module patterns or guarded commands, and validate that repeated runs produce no unnecessary changes.
- **Handler mismatch**: `poodle_fix.yml` notifies `Restart apache2`, but its declared handler is named `Restart apache`; this likely prevents the intended Apache restart. Normalize handler names and add an integration test that proves the effective configuration is active.
- **Cross-platform compliance mismatch**: The SSH InSpec control cites RHEL-08/STIG identifiers and checks `openssh-server` absence as an alternate branch, while the configured test platform is Ubuntu 20.04. Separate generic SSH assertions from platform-specific controls and define the supported OS matrix.
- **Certificate lifecycle**: Generated self-signed artifacts, hostname `myhost`, and fixed paths are not sufficient for production renewal, trust distribution, or multi-host operation. Establish certificate ownership, renewal, deployment, and rollback procedures.
- **Chef platform boundary**: The repository combines Ansible examples with scripts that provision Chef infrastructure. Decide whether this is a coexistence migration or a full Chef retirement; otherwise teams may migrate the web configuration while leaving an undocumented Chef control plane dependency.
- **Testing limitations**: The current tests verify a narrow web/TLS outcome but do not cover Apache syntax, certificate expiry, file permissions, idempotence, package availability, or handler execution. Add CI checks and a disposable integration environment before production rollout.

### Migration Order

1. **Baseline and ownership**: Inventory current users of the playbooks, preserve the InSpec acceptance criteria, rotate the exposed bootstrap password, and decide the target Ubuntu LTS and Ansible version.
2. **`website_https`**: Refactor the playbook into a reusable Apache HTTPS role, replace inline content with templates/files, parameterize site and certificate settings, and make package/service/site operations idempotent.
3. **`poodle_fix` / TLS policy**: Merge its intended TLS policy into the Apache role where possible, correct the handler mismatch, add Apache configuration validation, and verify supported TLS versions and ciphers against the security baseline.
4. **Validation modernization**: Run the existing InSpec controls in CI, resolve the Ubuntu/RHEL assumptions, add idempotence and security tests, and decide whether Kitchen/Vagrant should be replaced with Molecule or retained temporarily.
5. **Chef bootstrap decision**: If Chef is being retired, implement and test the replacement control-plane/bootstrap process before removing the scripts. If Chef remains, isolate the scripts, secure their inputs, pin and verify the CLI artifact, and document the operational handoff.
6. **Production rollout**: Pilot on a non-production host, compare Apache/TLS behavior, roll out gradually with rollback, and decommission legacy control-plane dependencies only after ownership and monitoring are confirmed.

### Assumptions

- The requested destination is Ansible; the repository already contains Ansible playbooks, so this plan treats the work as refactoring, hardening, and standardizing rather than translating Chef recipes.
- No `Berksfile`, `Policyfile.rb`, Chef `metadata.rb`, Puppet metadata, PowerShell manifests, Salt states, or Ansible inventory/requirements file were present in the supplied tree.
- `website_https.yml` and `poodle_fix.yml` are the complete Ansible configuration scope; unlisted external inventories, roles, CI pipelines, and vault files may alter behavior.
- Ubuntu 20.04 is the intended test OS because it is explicitly configured in Kitchen; production OS/version and Apache package repository policy are not specified.
- Vagrant is the test VM driver, but its provider and production virtualization/cloud platform are unknown.
- `myhost` is a test inventory name, not necessarily a production hostname.
- The self-signed certificate and Hello World site are demonstration content unless the owner confirms otherwise.
- The exposed password in the Chef bootstrap scripts is assumed unsafe and should be considered compromised until rotated; no evidence was found about whether these scripts have already been executed.
- The purpose of deploying Chef Automate/Infra Server during an Ansible migration is ambiguous. A product-retirement decision and service ownership review are required.
- The InSpec SSH control’s RHEL/STIG metadata does not establish RHEL support; OS-specific compliance requirements need confirmation.
- No availability, rollback, certificate authority, monitoring, inventory source, secrets manager, or change-management requirements were provided.
- Timeline estimates exclude building a replacement Chef control plane, migrating unrelated Chef assets, or upgrading the operating system.
