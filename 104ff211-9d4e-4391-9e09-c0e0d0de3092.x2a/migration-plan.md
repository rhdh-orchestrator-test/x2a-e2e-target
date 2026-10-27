# MIGRATION FROM CHEF ECOSYSTEM TO ANSIBLE

## Executive Summary

This repository is not a conventional Chef cookbook repository. It contains two Ansible playbooks, Chef InSpec verification tests, a Test Kitchen configuration using the Ansible provisioner, and shell scripts that bootstrap Chef Automate and/or Chef Infra Server. No `recipes/`, `metadata.rb`, `Berksfile`, `Policyfile.rb`, or other Chef cookbook structure is present, so there are no Chef cookbooks to convert directly.

The practical migration is therefore a small, focused transition from Chef tooling and Chef infrastructure bootstrap to an Ansible-managed web-server and platform workflow. The existing web configuration already provides a useful Ansible starting point: Ubuntu 20.04, Apache, a self-signed TLS certificate, a sample site, and TLS/HTTPS verification. The main effort is hardening and productionizing the existing playbooks, replacing imperative shell bootstrap steps where appropriate, and deciding whether the Chef server/Automate deployment is still required. A single engineer could complete a proof of concept in approximately 3–5 working days and a reviewed, secure, repeatable implementation in approximately 1–2 weeks, assuming no need to reproduce Chef Automate itself in Ansible.

## Module Migration Plan

This repository contains Chef ecosystem assets and Ansible examples, but no standalone Chef cookbooks that require individual recipe migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only paths observed in the supplied repository tree are listed below. The entries are migration units rather than inferred Chef cookbook modules.

- **website_https.yml**:
    - Description: An Ansible playbook for configuring an Apache HTTPS virtual host on `myhost`, installing a pinned Apache package and supporting OpenSSL packages, creating a self-signed certificate, deploying a Hello World site, enabling SSL, and disabling the default virtual host.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible
    - Key Features: Ubuntu/Debian `apt` installation, Apache virtual-host configuration, generated private key/CSR/self-signed certificate, site content deployment, Apache module/site activation, service handlers
    - Migration status: Already Ansible; refactor into a role or collection and harden rather than translate from Chef.

- **poodle-fix**:
    - Description: An Ansible playbook that restricts Apache SSL protocol configuration to TLS 1.2 and restarts Apache and SSH when the configuration changes.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible
    - Key Features: Regex replacement in Apache SSL configuration, TLS protocol restriction, service notifications
    - Migration status: Already Ansible; merge into the web-server role or retain as a separately invoked hardening task after validating current TLS policy.

- **website_https_verify**:
    - Description: Chef InSpec verification profile for checking HTTPS availability, Hello World content, disabled SSLv3, and enabled TLS 1.2.
    - Path: `chef-and-ansible/tests/website_https_verify.rb`
    - Technology: Chef InSpec
    - Key Features: Port 443 check, HTTPS response check, SSL protocol assertions
    - Migration status: Convert to Ansible Molecule/pytest tests, Testinfra, or an external compliance test suite; preserve these checks as acceptance criteria.

- **ssh_profile**:
    - Description: Chef InSpec control asserting that SSH root login is not permitted, with a package-related alternative assertion.
    - Path: `chef-and-ansible/tests/ssh_profile.rb`
    - Technology: Chef InSpec
    - Key Features: `PermitRootLogin` policy check, SSH compliance metadata and severity tags
    - Migration status: Convert to an Ansible hardening task plus an idempotent compliance test. Review the existing alternative assertion because it appears to treat the presence of `openssh-server` as a compliant condition, which is not equivalent to disabling root login.

- **Chef platform bootstrap (combined deployment variants)**:
    - Description: Shell-based bootstrap procedures that install the latest Chef Automate CLI, deploy Chef Automate with Infra Server or Infra Server alone, create a Chef user and organization, and emit PEM credentials.
    - Path: `setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`
    - Technology: Bash and Chef Automate/Infra Server
    - Key Features: Hostname and kernel tuning, remote CLI download, Chef product deployment, user/org creation, generated user and validator keys
    - Migration status: Not a cookbook. Replace only if the target state no longer needs Chef Server/Automate; otherwise retain as a separately governed legacy/platform bootstrap or automate it with Ansible modules and vendor-supported procedures.

### Infrastructure Files

- `README.md`: Repository-level description of Chef examples. Migration consideration: update to identify the Ansible ownership model, supported OS, test commands, and whether Chef platform deployment remains supported.
- `chef-and-ansible/README.md`: Describes using Chef InSpec with Ansible for continuous compliance. Migration consideration: revise if InSpec is being retired; otherwise document the deliberate coexistence of Ansible provisioning and InSpec verification.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, the Ansible playbook provisioner, Ubuntu 20.04, and InSpec verification. Migration consideration: decide whether to retain Test Kitchen/Vagrant or move to Ansible Molecule and a CI-managed Ubuntu test target.
- `chef-and-ansible/website_https.yml`: Primary web-server provisioning playbook and the main Ansible migration baseline.
- `chef-and-ansible/poodle_fix.yml`: TLS hardening playbook; should become part of the same role's security profile or a clearly ordered hardening play.
- `chef-and-ansible/tests/ssh_profile.rb`: SSH compliance control to preserve as a test requirement during conversion.
- `chef-and-ansible/tests/website_https_verify.rb`: HTTPS/TLS acceptance tests to preserve during conversion.
- `setup-automate/deploy-automate.sh`: Chef Automate plus Infra Server bootstrap; contains sensitive bootstrap inputs and external installation behavior.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server-only bootstrap; has the same credential and supply-chain concerns.

### Target Details

- **Operating System**: Ubuntu 20.04 is explicitly used by `kitchen.yml`. The playbooks use `apt`, `/etc/apache2`, `a2ensite`, and `a2enmod`, so the immediate target is Debian-family Linux, specifically Ubuntu 20.04 for the tested path. Validate support before moving to a newer Ubuntu LTS or another distribution.
- **Virtual Machine Technology**: Vagrant is specified as the Test Kitchen driver. The deployment scripts describe an on-premises or cloud VM but do not identify a cloud provider or hypervisor.
- **Cloud Platform**: Not specified. The Chef bootstrap scripts are intended for either on-premises or cloud VMs and contain no provider-specific modules, metadata endpoints, or SDK configuration.

## Migration Approach

### Key Dependencies to Address

- **Apache HTTP Server 2.4.41-4ubuntu3.10**: The playbook pins an Ubuntu package version. Replace with an explicit variable and a supported repository/version policy; avoid retaining a stale security-sensitive pin without confirming repository availability and patch status.
- **OpenSSL and Python OpenSSL support**: The playbook installs `openssl` and `python3-openssl` and uses Ansible OpenSSL modules. Use fully qualified collection names where practical and test certificate generation on the selected Ansible version.
- **Ansible version**: `kitchen.yml` requests `latest`, which is non-reproducible. Pin the controller Ansible version and required collections in a `requirements.yml`/execution-environment definition.
- **Vagrant and Test Kitchen**: Current integration testing depends on Vagrant and the Test Kitchen Ansible provisioner. Either pin and maintain that toolchain or migrate tests to Molecule with a supported driver/container or VM backend.
- **Chef InSpec**: Existing verification depends on InSpec. Preserve it during a staged transition, or replace the controls with Molecule/Testinfra and an Ansible hardening role after parity is demonstrated.
- **Chef Automate CLI and Chef Infra Server**: The shell scripts download a current CLI from `packages.chef.io` and invoke vendor commands. There is no equivalent requirement to install Chef components in an Ansible-only target; make this a deliberate platform decision rather than silently translating it.
- **Vagrant Ubuntu 20.04 image**: Ensure the image is maintained, checksummed, and available to CI. Plan an OS lifecycle upgrade because Ubuntu 20.04 is an aging baseline.

### Security Considerations

- **Hardcoded bootstrap password**: Both deployment scripts contain `userpassword='password'`. Remove it immediately, rotate any credentials used with these scripts, and supply secrets through Ansible Vault, an external secret manager, or a protected CI secret. Never commit generated PEM files.
- **Chef credential material**: The scripts create user and organization PEM files (`${username}.pem` and `${orgname}-validator.pem`). Define secure ownership, permissions, storage, rotation, revocation, and cleanup procedures before retaining this workflow.
- **TLS private key and certificate**: `website_https.yml` generates `/etc/apache2/certs/apache.key`, CSR, and self-signed certificate. Protect the key with restrictive permissions, consider a dedicated certificate authority or managed certificate for production, and do not use self-signed certificates where clients require trust validation.
- **TLS policy**: The Poodle fix disables protocols other than TLS 1.2, while the verification explicitly checks SSLv3 disabled and TLS 1.2 enabled. Confirm whether TLS 1.3 should also be enabled, validate cipher policy, and avoid a blanket replacement that conflicts with distribution-managed Apache configuration.
- **SSH hardening**: Preserve the `PermitRootLogin` control in an Ansible hardening role, ensure the SSH service name is correct on Ubuntu (`ssh` versus `sshd`), and test access before applying changes to remote systems.
- **Unsafe remote installation**: The shell scripts pipe a downloaded archive through `gunzip` and execute it without visible checksum/signature verification. Replace with a verified, pinned artifact or vendor repository and use Ansible download/unarchive steps with integrity checks if Chef remains required.
- **File modes and ownership**: Review certificate directory mode `0640`, key/certificate ownership, Apache configuration permissions, and web-root ownership. Make permissions explicit and verify that the Apache service account can read only what it needs.
- **Privilege escalation**: The playbooks use `remote_user: root` and `become: yes`. Standardize on a non-root administrative account with narrowly controlled `become`, and define inventory/group variables rather than embedding access assumptions in playbooks.
- **Credential patterns by asset**: No Chef encrypted data bags or Chef Vault references were observed. Visible secrets are the hardcoded Chef bootstrap password, generated Chef PEM credentials, and TLS private key material. Treat all as sensitive and scan repository history for prior exposure.

### Technical Challenges

- **No source cookbook implementation exists**: There is no Chef recipe/resource behavior to translate. Establish the desired end state from the existing playbooks and operational requirements, then avoid creating a fictitious cookbook inventory.
- **Imperative Apache commands**: `a2dissite` and `a2ensite` are invoked with `command`, which may not be fully idempotent. Replace with a purpose-built Apache role or guarded commands and validate enabled-site/module state.
- **Handler naming and notifications**: The TLS playbook notifies `Restart apache2` and `Restart sshd`, but the declared handler is named `Restart apache`; this mismatch can cause a playbook failure. Normalize handler names and use the platform-correct SSH service name.
- **Configuration correctness**: The inline HTML appears malformed (`</title>/head>`), and Apache configuration syntax/compatibility should be validated with `apachectl configtest` before restart. Move large inline content into templates/files.
- **Certificate lifecycle**: Self-signed certificate generation is suitable for a demonstration but needs renewal, trust distribution, SAN handling, and service reload behavior for production.
- **Cross-platform assumptions**: All web tasks are Debian/Ubuntu-specific. Add OS-family assertions or separate role variables before supporting RHEL-like systems.
- **Testing transition**: InSpec controls contain compliance metadata that must not be lost when converting to Molecule/Testinfra. Build equivalent tests for HTTPS, content, protocol policy, and SSH configuration before changing implementation.
- **Chef platform scope**: Replacing Chef Infra Server/Automate may be an organizational/platform migration, not merely a playbook conversion. Confirm whether Ansible Automation Platform, AWX, or another control plane is the intended replacement and define inventory, RBAC, audit, and job scheduling requirements.

### Migration Order

1. **Baseline and security remediation**: Inventory affected hosts, rotate the exposed bootstrap password, preserve the InSpec checks as acceptance criteria, pin Ansible/tool versions, and decide whether Chef Server/Automate is in or out of scope.
2. **Web-server role**: Refactor `website_https.yml` into an idempotent Apache role with variables for package version, vhost, document root, certificate source, and service name. Replace inline content with templates/files and add syntax/configuration validation.
3. **TLS and SSH hardening**: Integrate `poodle_fix.yml` and the SSH control into a controlled hardening role/profile. Test TLS 1.2/1.3 policy, root-login behavior, and rollback/access recovery.
4. **Automated validation**: Run the equivalent HTTPS and SSH checks in Molecule or the chosen CI framework against Ubuntu 20.04, then test the selected newer supported Ubuntu LTS.
5. **Chef platform decision and transition**: If Chef Automate/Infra Server is retired, replace its bootstrap and operational responsibilities with the selected Ansible control plane. If retained, isolate the scripts as legacy platform automation and secure their credentials/artifact verification.
6. **Documentation and rollout**: Update READMEs, ownership, runbooks, inventory conventions, secret-management procedures, and rollback steps; pilot on non-production hosts before broad deployment.

### Assumptions

- The requested migration concerns the assets in this tree, not an unseen Chef organization, cookbook repository, or production Chef Server.
- No Chef cookbooks, recipes, metadata manifests, Berkshelf files, Policyfiles, or cookbook dependencies are present in the supplied tree.
- The existing Ansible playbooks represent the intended desired state for the demonstration website.
- Ubuntu 20.04 is the initial target because it is the only explicit platform declaration; support for other operating systems is not assumed.
- Vagrant is used for local testing, but the production VM platform is unspecified.
- No cloud provider is implied by the phrase “on-prem or cloud VM.”
- The hardcoded sample password may have been used in real environments; it is assumed compromised until proven otherwise and must be rotated.
- Generated PEM files and TLS keys may exist outside the repository or in shell history; those locations require separate investigation.
- The final target may retain Chef InSpec temporarily for compliance verification; the team must choose whether to retire it.
- Chef Automate/Infra Server replacement is assumed to be a separate workstream unless stakeholders explicitly require its full functional replacement by Ansible.
- Package versions, Apache service names, TLS requirements, certificate trust model, DNS names, and production inventory are not fully specified and must be confirmed during implementation.
- The timeline estimate assumes a small demonstration scope, accessible test hosts, and no requirement to reproduce Chef Automate's complete UI, compliance, reporting, or policy features.
