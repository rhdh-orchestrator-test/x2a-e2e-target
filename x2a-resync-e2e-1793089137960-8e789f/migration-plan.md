# MIGRATION FROM CHEF-RELATED AUTOMATION AND ANSIBLE EXAMPLES TO ANSIBLE

This repository is a small, mixed technology example rather than a conventional Chef cookbook repository. The operational website configuration is already implemented as an Ansible playbook, while Chef appears in the surrounding documentation, Chef InSpec verification tests, and shell scripts that install Chef Automate/Infra Server. There are no discovered Chef cookbooks, Puppet modules, Salt states, PowerShell modules, Berksfiles, Policyfiles, or Chef `metadata.rb` files to translate. The practical migration is therefore an Ansible standardization and hardening effort, with Chef server/Automate bootstrap either retired or isolated as a separate platform concern. A focused implementation should take approximately 2–5 working days for a proof of concept and 1–2 weeks for production hardening, testing, secret integration, and team handoff.

## Module Migration Plan

This repository contains Ansible playbooks, Chef InSpec compliance tests, and Chef platform bootstrap scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that provisions an Apache HTTPS “Hello World” site, installs Apache and OpenSSL-related packages, creates a self-signed certificate, writes a virtual host and website content, enables the site and SSL module, and restarts services.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible
    - Key Features: Ubuntu Apache package pinning, self-signed key/CSR/certificate generation, TLS virtual host, static content deployment, `a2ensite`/`a2enmod` activation
    - Migration status: Retain as the functional baseline, then refactor into a reusable role with variables, templates, handlers, idempotent modules, and external certificate management.

- **poodle_fix**:
    - Description: Ansible playbook intended to restrict Apache SSL protocols to TLS 1.2 and restart Apache and SSH after the change.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible
    - Key Features: Apache SSL configuration replacement, TLS hardening intent, service restart notifications
    - Migration status: Retain the security intent but correct the handler notification mismatch (`Restart apache2` is notified while the declared handler is `Restart apache`) and validate the configuration before restarting.

- **Chef InSpec SSH compliance profile**:
    - Description: InSpec control verifying that SSH root login is not permitted, with a fallback assertion concerning the OpenSSH server package.
    - Path: `chef-and-ansible/tests/ssh_profile.rb`
    - Technology: Chef InSpec/Ruby
    - Key Features: `PermitRootLogin` control, severity and STIG metadata, SSH configuration inspection
    - Migration status: Convert the control into Ansible assertions/check mode or an Ansible-focused compliance framework such as Molecule/verifier, keeping the control metadata in compliance documentation. The package fallback appears logically unusual and requires owner confirmation.

- **website_https_verify**:
    - Description: InSpec verification of HTTPS port availability, successful local HTTPS response, expected page content, disabled SSLv3, and enabled TLS 1.2.
    - Path: `chef-and-ansible/tests/website_https_verify.rb`
    - Technology: Chef InSpec/Ruby
    - Key Features: Port and HTTP checks, TLS protocol checks, certificate verification intentionally disabled for the test
    - Migration status: Re-express as Ansible Molecule tests and/or Testinfra/pytest checks. Keep certificate validation enabled in production-oriented tests once a trusted certificate is used.

- **Chef Automate bootstrap**:
    - Description: Bash bootstrap that sets host kernel parameters, downloads the current Chef Automate CLI, deploys Chef Automate plus Chef Infra Server, and creates a Chef user, organization, and PEM credentials.
    - Path: `setup-automate/deploy-automate.sh`
    - Technology: Bash/Chef Automate/Chef Infra Server
    - Key Features: Combined Automate and Infra Server deployment, CLI download, organization/user creation, generated PEM files
    - Migration status: Do not translate blindly into a normal application role. Decide whether Chef services are being decommissioned; if retained, model this as a separately owned, vaulted Ansible platform role with supported package/version pinning.

- **Chef Infra Server bootstrap**:
    - Description: Bash bootstrap for a Chef Infra Server-only deployment with the same host tuning, user/org creation, and credential generation flow.
    - Path: `setup-automate/deploy-chef-server.sh`
    - Technology: Bash/Chef Infra Server
    - Key Features: Infra Server deployment, system tuning, user and organization provisioning, PEM output
    - Migration status: Treat as a separate optional platform migration. If Chef is retired, replace its configuration-management responsibility with Ansible Automation Platform/control node practices rather than recreating Chef Server.

### Infrastructure Files

- `README.md`: Repository-level description of Chef examples; provides context but no deployable configuration.
- `chef-and-ansible/README.md`: Describes the Ansible and Chef InSpec compliance example and should be updated to document the post-migration workflow.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using the Vagrant driver, Ansible playbook provisioner, Ubuntu 20.04 platform, and InSpec verifier. It is the main test orchestration file and should be replaced or supplemented with Ansible Molecule and a supported CI test matrix.
- `chef-and-ansible/website_https.yml`: Primary deployment playbook; see module inventory.
- `chef-and-ansible/poodle_fix.yml`: TLS hardening playbook; see module inventory.
- `chef-and-ansible/tests/`: InSpec acceptance tests that define the current compliance expectations.
- `setup-automate/deploy-automate.sh`: Chef platform bootstrap; requires retirement or isolated replacement planning.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server bootstrap; requires retirement or isolated replacement planning.

### Target Details

- **Operating System**: Ubuntu 20.04 is explicitly specified in `chef-and-ansible/kitchen.yml`; the playbooks use `apt`, `/etc/apache2`, `a2ensite`, and `a2enmod`. The InSpec SSH control contains RHEL 8 STIG identifiers, but that is compliance metadata rather than evidence of the deployment OS. Confirm whether Ubuntu 20.04 remains supported or whether the target should be upgraded to Ubuntu 22.04/24.04.
- **Virtual Machine Technology**: Vagrant is specified by Test Kitchen. The underlying provider is not specified.
- **Cloud Platform**: Not specified. The bootstrap comments allow on-premises or cloud VMs, but no provider-specific resources are present.

## Migration Approach

### Key Dependencies to Address

- **Ansible**: Already used by the website playbooks. Standardize on supported fully qualified collection names and a supported Ansible version; replace deprecated short module syntax where appropriate.
- **Apache 2.4.41-4ubuntu3.10**: The playbook pins this Ubuntu package version. Decide whether reproducibility requires an internal repository/package pin or whether a supported current Apache package should be used.
- **OpenSSL and `python3-openssl`**: Required for certificate generation. Prefer `community.crypto` modules with an explicitly managed collection dependency and use a trusted CA or certificate service for production.
- **Vagrant/Test Kitchen/InSpec**: Current integration test stack. Migrate to Molecule with a Vagrant or container driver, and retain equivalent TLS and SSH assertions in CI.
- **Chef Automate CLI and Chef Infra Server**: Downloaded dynamically from the “current/latest” URL. Either remove them with Chef retirement or pin a supported release and package source in an isolated Ansible role.
- **Chef-generated PEM credentials**: Must not be treated as ordinary playbook artifacts. Store or rotate them through an approved secrets system if Chef remains.

### Security Considerations

- **Hardcoded credentials**: Both bootstrap scripts contain a literal user password (`password`), user identity data, and organization data. Remove all secrets from source, rotate any exposed credential, and use Ansible Vault or an enterprise secret manager with short-lived credentials.
- **Generated private keys and PEM files**: The scripts create user and organization PEM files; protect them with restrictive permissions, avoid logging, define ownership and lifecycle, and securely destroy obsolete copies.
- **TLS private key**: `website_https.yml` creates `/etc/apache2/certs/apache.key`, but does not explicitly set restrictive key permissions. Set owner/group/mode, protect the directory, and avoid self-signed certificates outside test environments.
- **Certificate trust and validation**: The InSpec HTTPS test uses `ssl_verify: false`, which is acceptable only for the self-signed test certificate. Production tests and clients should validate the certificate chain, hostname, expiry, and key usage.
- **TLS protocol hardening**: The intended TLS 1.2-only policy should be reviewed against current organizational standards, including TLS 1.3 where supported. Disable obsolete protocols through a managed Apache configuration and test before service restart.
- **Privilege and SSH**: Playbooks run as `root` with `become: yes`, and the compliance profile checks root SSH login. Define the approved administrative account, sudo policy, SSH configuration ownership, and a recovery path before enforcing changes.
- **Unsafe command usage**: `a2dissite` and `a2ensite` are invoked through `command`; use idempotent Ansible modules or guarded commands and validate Apache configuration before handlers restart services.
- **Supply-chain risk**: The bootstrap scripts pipe a remote “latest” download into `gunzip` and execute it. Replace with a version-pinned artifact, checksum/signature verification, and controlled repository.
- **Configuration correctness**: The Apache certificate directory is created with mode `0640`, which is not a directory execute/search permission for typical access patterns. Define intended directory mode explicitly. Also review the virtual host content and malformed HTML (`</head>` is missing its opening `<`), even though this is not a security control.

### Technical Challenges

- **Already-partially-migrated source**: The main deployment is already Ansible, so the work is less a Chef-to-Ansible translation and more a role, testing, security, and lifecycle refactor. Establish a clear target operating model before rewriting.
- **Chef platform decision**: Automate and Infra Server are infrastructure products, not application modules. Retiring Chef may require inventory, credential, policy, and team-process migration beyond these files; retaining it creates a separate operational dependency.
- **Cross-platform compliance expectations**: Ubuntu deployment settings coexist with RHEL 8 STIG labels. Confirm the compliance baseline and implement OS-specific Ansible variables/tests rather than assuming one platform.
- **Idempotence and handler behavior**: Direct site/module commands and the incorrect handler name can produce failed or inconsistent runs. Refactor activation and restart behavior and test repeated execution.
- **Certificate lifecycle**: Self-signed certificates are suitable for a lab only. Production issuance, renewal, distribution, trust stores, and revocation need ownership and integration with a PKI or ACME service.
- **Version drift**: “Latest” Chef CLI and unqualified test dependencies reduce repeatability. Establish version locks, CI compatibility testing, and upgrade ownership.
- **Testing migration**: Test Kitchen plus InSpec currently supplies the acceptance contract. Preserve the controls while moving execution to Molecule/pytest or an approved Ansible compliance pipeline.

### Migration Order

1. **Baseline and decision**: Confirm the supported Ubuntu release, Apache version, certificate authority, Chef retirement/retention decision, and target Ansible execution platform. Inventory any environments not represented by this repository.
2. **Website role**: Convert `website_https.yml` into a reusable Apache HTTPS role with variables, Jinja templates, proper file modes, package policy, idempotent enablement, and safe handlers. This is the clearest low-risk value path.
3. **TLS hardening**: Refactor `poodle_fix.yml` into the role or a dedicated hardening role, fix notification names, add syntax/config validation, and test both first and repeated runs.
4. **Compliance tests**: Port the HTTPS and SSH InSpec controls into the chosen Ansible test framework, correcting the OpenSSH package assertion and separating Ubuntu/RHEL expectations.
5. **CI and documentation**: Replace or supplement Kitchen with Molecule, test supported OS versions, add linting/security scanning, and document variables, inventories, certificate sources, and rollback procedures.
6. **Chef platform disposition**: If Chef is retired, decommission the bootstrap scripts and migrate remaining Chef organizations, credentials, and workloads through a controlled transition. If retained, create a separately owned, pinned, vaulted role for Chef server operations.

### Assumptions

- The file listing is complete and no hidden cookbook, metadata, Berksfile, Policyfile, Puppet, Salt, or PowerShell content exists outside the shown paths.
- No Chef cookbook modules were found; the repository’s deployable configuration is the two Ansible YAML playbooks.
- Ubuntu 20.04 is the intended lab target because it is the only explicit platform declaration.
- Vagrant is used for tests, but its provider and production virtualization platform are unknown.
- The self-signed certificate and local Hello World site are demonstration assets, not production requirements.
- The desired end state is Ansible-managed hosts; whether Chef Automate/Infra Server itself must remain is unresolved.
- The `myhost` inventory group, SSH access method, and remote user policy are defined externally and were not provided.
- Certificate issuance, DNS, firewall rules, Apache module prerequisites, and package repository policy are not fully represented in the playbooks.
- The InSpec RHEL/STIG identifiers may be documentation copied from a broader baseline and do not prove that RHEL is a deployment target.
- Existing PEM files, passwords, or certificates may already have been exposed by prior script execution; security teams should assume compromise until rotation is confirmed.
- Timeline estimates assume one small team familiar with Ansible and access to the target hosts; production change approval, PKI integration, and Chef estate retirement can extend the schedule.
- Teams should assign separate owners for Ansible roles, compliance/test conversion, PKI/secrets, CI, and Chef platform disposition, with a shared acceptance checklist and staged rollout.