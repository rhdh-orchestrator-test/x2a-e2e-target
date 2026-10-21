# MIGRATION FROM ANSIBLE PLAYBOOKS AND CHEF AUTOMATE SCRIPTS TO ANSIBLE

This is a small hybrid example repository rather than a conventional Chef cookbook repository. The operational configuration is already expressed as two Ansible playbooks (`website_https.yml` and `poodle_fix.yml`); the remaining Chef-related content provisions Chef Infra Server/Automate and the test suite uses Chef InSpec. The migration is therefore primarily a consolidation and hardening effort: retain or refactor the existing Ansible configuration, replace the Chef control-plane bootstrap where it is no longer required, and preserve the InSpec compliance intent in Ansible tests or a defined compliance pipeline. A focused implementation should take approximately 1–2 weeks for one engineer, including testing and security review; adopting a production-grade PKI, secrets platform, and CI/CD integration may extend this to 3–5 weeks.

## Module Migration Plan

This repository contains Ansible playbooks, Chef infrastructure bootstrap scripts, and Chef InSpec tests that need individual migration planning. No Puppet modules, Chef cookbooks (`recipes/default.rb`), PowerShell modules, or Salt states were found in the supplied tree.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths below were present in the supplied repository tree and were reviewed directly.

- **website_https**:
    - Description: An Ansible playbook that installs and configures Apache HTTP Server on an Ubuntu host, publishes a static Hello World site, creates a self-signed TLS key/CSR/certificate, and enables an HTTPS virtual host.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible
    - Key Features: Ubuntu apt package installation, Apache virtual-host configuration, local certificate generation, site enablement, SSL module activation, and service handlers.

- **poodle_fix**:
    - Description: An Ansible remediation playbook intended to restrict Apache SSL protocol configuration to TLS 1.2.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible
    - Key Features: Replacement of the Apache `SSLProtocol` setting and service restart notifications; it is a targeted TLS-hardening task rather than a complete server role.

- **chef-infra-server-bootstrap**:
    - Description: Bash-based bootstrap for Chef Infra Server, creating a Chef user and organization and writing user and validator PEM files.
    - Path: `setup-automate/deploy-chef-server.sh`
    - Technology: Bash/Chef Infra Server
    - Key Features: Hostname and kernel tuning, downloaded Chef Automate CLI, Infra Server deployment, user creation, organization creation, and credential-file generation.

- **chef-automate-bootstrap**:
    - Description: Bash-based bootstrap for a combined Chef Automate and Chef Infra Server installation.
    - Path: `setup-automate/deploy-automate.sh`
    - Technology: Bash/Chef Automate and Chef Infra Server
    - Key Features: Combined product deployment, hostname and kernel tuning, administrative user creation, organization creation, and PEM credential generation.

- **ssh-root-login-compliance**:
    - Description: Chef InSpec control verifying that SSH root login is not enabled, with an alternate package-based assertion.
    - Path: `chef-and-ansible/tests/ssh_profile.rb`
    - Technology: Chef InSpec
    - Key Features: SSH daemon configuration check and security-control metadata for RHEL 8/STIG-style compliance.

- **website-https-compliance**:
    - Description: Chef InSpec checks for HTTPS availability and expected site content, plus TLS protocol validation.
    - Path: `chef-and-ansible/tests/website_https_verify.rb`
    - Technology: Chef InSpec
    - Key Features: Port 443 listening, HTTP 200 response, Hello World content, SSLv3 disabled, and TLS 1.2 enabled.

### Infrastructure Files

- `README.md`: Repository-level description identifying the project as Chef examples; migration documentation should clarify which examples remain relevant after consolidation.
- `chef-and-ansible/README.md`: Describes the InSpec-with-Ansible compliance use case; retain as the rationale for the test and compliance design.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, an Ansible playbook provisioner, Ubuntu 20.04, and InSpec verification. It is a development/test harness, not production deployment configuration.
- `chef-and-ansible/website_https.yml`: Main web-server provisioning playbook and the principal Ansible migration artifact.
- `chef-and-ansible/poodle_fix.yml`: Separate TLS remediation playbook that should be folded into a reusable role or baseline hardening role.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec SSH compliance control to preserve, translate, or run as an external compliance test.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec functional and TLS checks for the web service.
- `setup-automate/deploy-automate.sh`: Chef Automate plus Infra Server bootstrap; replace only if Chef control-plane services are out of scope for the target estate.
- `setup-automate/deploy-chef-server.sh`: Chef-only control-plane bootstrap; its lifecycle and generated credentials require an explicit replacement decision.

## Target Details

- **Operating System**: Ubuntu 20.04 is explicitly declared in `kitchen.yml`. The playbooks use `apt`, Apache paths such as `/etc/apache2`, and the `apache2` service, so the immediate target is Debian/Ubuntu. The InSpec SSH control references RHEL 8/STIG identifiers, but that is compliance metadata rather than evidence that the playbook targets RHEL. Confirm whether Ubuntu 20.04 remains supported or whether the target should be upgraded to a newer Ubuntu LTS.
- **Virtual Machine Technology**: Vagrant is specified as the Kitchen driver. The runtime platform behind Vagrant is not specified; do not assume VirtualBox, VMware, or libvirt without environment confirmation.
- **Cloud Platform**: Not specified. The shell comments say on-prem or cloud VM, but no provider-specific SDK, metadata endpoint, or provisioning configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Ansible runtime and collections**: `kitchen.yml` requests the latest Ansible and the playbook uses `openssl_privatekey`, `openssl_csr`, and `openssl_certificate`. Pin a supported `ansible-core` version and explicitly declare the collection providing these modules (typically `community.crypto`), rather than relying on an unpinned latest runtime.
- **Ubuntu apt repositories and Apache 2.4**: The playbook pins `apache2` to `2.4.41-4ubuntu3.10`, which is tied to Ubuntu 20.04 repository packaging. Replace with a controlled package/version policy and validate availability in the target mirror.
- **OpenSSL/PyOpenSSL**: `curl`, `openssl`, and `python3-openssl` are installed for certificate generation. Prefer Ansible crypto modules with managed Python prerequisites and define whether certificates are ephemeral test certificates or production PKI-issued certificates.
- **Vagrant, Test Kitchen, and InSpec**: These support local verification only. Decide whether to retain them, migrate to Molecule plus Ansible-native assertions, or retain InSpec as a separate compliance gate.
- **Chef Automate CLI and Chef Infra Server**: The shell scripts download the latest CLI directly from `packages.chef.io` and invoke Chef product deployment commands. If Chef is being removed, replace this control-plane function with Ansible Automation Platform/AWX, Git-based inventories, CI/CD, and a secrets system. If Chef remains, document it as an external dependency rather than attempting to model it as an Apache role.
- **Vagrant guest prerequisites**: The Kitchen configuration assumes a Vagrant Ubuntu guest reachable as `myhost` and usable by the Ansible provisioner. Recreate equivalent inventory, SSH, privilege escalation, and test lifecycle settings in the target automation platform.

### Security Considerations

- **Hardcoded administrative password**: Both bootstrap scripts contain `userpassword='password'`. Remove it immediately, rotate any credentials generated from it, and obtain credentials through Ansible Vault, an external secret manager, or an interactive/CI secret injection mechanism.
- **Generated Chef private keys**: The scripts write user and organization validator PEM files (`*.pem`). Treat them as private credentials, protect file permissions, avoid workspace persistence and source control, and define revocation/rotation procedures. If Chef is retired, securely destroy obsolete keys.
- **Untrusted shell download**: Both scripts pipe a live download from `packages.chef.io` directly into `gunzip` and execute the result. Replace with a pinned, checksum/signature-verified artifact and controlled repository, or remove the bootstrap entirely.
- **Root and privilege use**: Playbooks connect as `root` and use `become: yes`; the bootstrap scripts use `sudo`. Use a dedicated least-privileged automation account, narrowly scoped sudo, SSH keys, and host-key verification in production.
- **TLS key and certificate handling**: The web playbook creates a private key and self-signed certificate on the target. The certificate directory is assigned mode `0640`, which may prevent directory traversal/access as intended but should be explicitly reviewed; the key file mode is not explicitly set. Set restrictive key permissions and use a real CA/ACME or enterprise PKI for production. Do not expose private keys in logs or artifacts.
- **TLS policy**: The intended policy is TLS 1.2 only and SSLv3 disabled. Validate the resulting Apache configuration against current organizational policy; consider TLS 1.3 where supported and remove obsolete protocols/ciphers through a tested hardening role.
- **SSH service changes**: Notifications restart `sshd` while changing web/TLS configuration. This is unnecessary for most Apache changes and can disrupt access. Only modify SSH through a dedicated, tested hardening task with console/recovery access.
- **Credential patterns by module**: `website_https` contains generated TLS private-key material on hosts but no embedded password; `poodle_fix` contains no visible credentials; both Chef bootstrap scripts contain a hardcoded password and generate Chef PEM credentials; the InSpec tests contain no credentials.

### Technical Challenges

- **Already-partial Ansible migration**: The repository is not a Chef cookbook conversion. The main service is already Ansible, so the challenge is normalization, testing, and lifecycle ownership rather than translating Chef resources. Mitigate by creating a versioned Apache role and a separate security baseline role.
- **Idempotency and module compatibility**: `a2ensite`, `a2dissite`, and `a2enmod` are invoked through `command`, and module names/parameters may vary by Ansible collection version. Replace commands with idempotent modules where possible, use `changed_when`/guards where necessary, and run repeated convergence tests.
- **Handler inconsistencies**: `website_https.yml` notifies `Restart sshd` and `Restart apache`; `poodle_fix.yml` notifies `Restart apache2` but defines a handler named `Restart apache`, so the latter notification will not resolve. Correct names and avoid restarting SSH for web changes before production rollout.
- **Configuration quality and portability**: The inline HTML has a malformed `</head>` closing tag, Apache configuration syntax is legacy-style in places, and hard-coded Ubuntu paths/package versions limit portability. Move site and vhost content into templates/defaults and validate with `apache2ctl configtest`.
- **Certificate lifecycle**: Self-signed certificates are suitable for a disposable Kitchen test but not a production service. Establish issuance, renewal, trust distribution, and hostname/SAN requirements before migration acceptance.
- **Compliance test portability**: The SSH control uses RHEL/STIG identifiers while the tested platform is Ubuntu, and its alternate assertion treats an installed OpenSSH server as a failure even though the web test host necessarily needs SSH for provisioning. Reconcile the policy intent and platform-specific controls.
- **Chef control-plane replacement**: Removing Chef Automate/Infra Server may affect organization/user/key management and existing fleet workflows. Inventory consumers and perform a staged cutover; do not delete the bootstrap scripts until ownership and rollback are agreed.
- **Test harness modernization**: Kitchen uses `ansible_version: latest`, reducing reproducibility. Pin versions and add CI tests for convergence, Apache syntax, certificate properties, HTTP behavior, and TLS scans.

### Migration Order

1. **Baseline and inventory**: Confirm whether Chef Infra Server/Automate is still required, identify target Ubuntu LTS and supported Ansible versions, inventory consumers of generated Chef keys, and establish secret rotation.
2. **Test and compliance foundation**: Pin Ansible and collection versions, make Kitchen or a replacement test harness reproducible, and correct the InSpec platform/policy assumptions.
3. **Apache role migration/refactor**: Convert `website_https.yml` into a reusable role with variables for package policy, vhost, document root, certificate source, and service behavior. Add idempotency and configuration validation tests.
4. **TLS hardening**: Merge `poodle_fix.yml` into the role or a shared hardening role, correct handler behavior, eliminate unnecessary SSH restarts, and validate TLS policy across supported OS versions.
5. **Secrets and PKI integration**: Replace self-signed production certificates and hardcoded bootstrap credentials with Vault/secret-manager references and enterprise PKI/ACME issuance.
6. **Chef control-plane decision and cutover**: If Chef is retired, implement the replacement automation/control-plane workflow and migrate users, organizations, nodes, and keys in stages. If retained, isolate and harden the Chef bootstrap as a separately governed dependency.
7. **Decommission and operational handoff**: Run parallel validation, document rollback, remove obsolete credentials/artifacts, and hand ownership to platform, security, and application teams.

### Assumptions

- The requested destination is Ansible for infrastructure configuration; the repository’s existing Ansible playbooks are in scope for refactoring rather than wholesale translation.
- No Chef cookbooks, Berksfiles, Policyfiles, Puppetfiles, metadata manifests, or PowerShell modules were present in the supplied tree; dependency analysis is therefore based on the explicit playbook, Kitchen, shell, and InSpec files.
- Ubuntu 20.04 is the demonstrated test target, but its continued support and the production OS are not confirmed.
- Vagrant is used for local testing only; the production VM or cloud platform is unknown.
- The Chef Automate/Infra Server scripts may be examples rather than currently deployed production infrastructure; this must be confirmed before removal.
- The literal password in the scripts is assumed to be sample data, but it must be treated as compromised until proven otherwise.
- The self-signed certificate is assumed to be test-only; production certificate ownership, CA, renewal, and SAN requirements are unspecified.
- The intended SSH compliance policy, especially the package-based alternative in `ssh_profile.rb`, is ambiguous and requires security-owner clarification.
- The target inventory, host naming, SSH user, sudo policy, network access, and secret backend are not defined.
- The desired replacement for Chef Automate’s dashboards, compliance reporting, node management, and credential issuance is not specified.
- Timeline assumes one small Apache workload and cooperative access to target environments; multi-environment rollout, regulated compliance evidence, or a Chef fleet migration will increase duration.
- Team coordination should assign clear owners for Ansible role engineering, security/PKI, Chef platform transition, CI/test infrastructure, and production operations; require peer review for privilege, TLS, and secret changes; and use a staged dev-to-test-to-production promotion with documented rollback.
