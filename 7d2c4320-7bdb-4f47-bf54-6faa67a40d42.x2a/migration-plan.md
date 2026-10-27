# MIGRATION FROM CHEF/ANSIBLE EXAMPLES TO ANSIBLE

This repository is not a Chef cookbook repository despite the stated focus on Chef cookbooks. The reviewed tree contains two standalone Ansible playbooks, Chef InSpec compliance tests, and Bash installers for Chef Automate/Infra Server. No Chef cookbooks, recipes, `metadata.rb`, Berksfile, Policyfile, Puppet manifests, Salt states, or PowerShell modules were found. Consequently, the direct configuration migration to Ansible is effectively complete; the meaningful work is to normalize the existing playbooks into a maintainable Ansible project and decide whether the Chef platform bootstrap scripts and InSpec controls are also being retired or retained.

Scope is small (two playbooks and two tests), with low-to-moderate implementation complexity. A focused engineer could normalize and validate the Ansible content in approximately 2–5 working days, including testing and documentation. Replacing Chef Automate/Infra Server and establishing equivalent governance, secrets management, and compliance reporting is a separate platform project, likely 2–6 weeks depending on target architecture and organizational requirements.

## Module Migration Plan

This repository contains standalone Ansible playbooks and supporting Chef ecosystem tooling; it does not contain Chef cookbooks requiring recipe-by-recipe conversion.

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that installs a pinned Apache 2.4 package on Ubuntu, creates a self-signed TLS key/certificate, configures an HTTPS Hello World virtual host, deploys static web content, enables the SSL module/site, and restarts Apache and SSH.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible
    - Key Features: Ubuntu `apt` package management, Apache SSL, local certificate generation, virtual-host configuration, static website deployment, service handlers, InSpec verification.

- **poodle_fix**:
    - Description: Ansible hardening playbook that changes Apache SSL protocol configuration to disable all protocols except TLS 1.2 and restarts Apache and SSH when the file changes.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible
    - Key Features: SSL protocol hardening, configuration replacement, service notifications.

- **chef_platform_bootstrap_automate**:
    - Description: Bash deployment workflow for Chef Automate with Chef Infra Server, followed by creation of a Chef user and organization and generated PEM credentials.
    - Path: `setup-automate/deploy-automate.sh`
    - Technology: Bash/Chef Automate and Chef Infra Server
    - Key Features: downloads the latest Chef Automate CLI, deploys both products, creates an administrator and organization, writes user and validator keys.

- **chef_platform_bootstrap_infra_server**:
    - Description: Bash deployment workflow for Chef Infra Server only, including host tuning, CLI download, user creation, organization creation, and PEM key generation.
    - Path: `setup-automate/deploy-chef-server.sh`
    - Technology: Bash/Chef Infra Server
    - Key Features: Chef server bootstrap, organization/user provisioning, generated authentication keys, kernel/sysctl tuning.

- **website_https_compliance**:
    - Description: Chef InSpec profile checks that HTTPS is listening, the Hello World page returns HTTP 200 and expected content, SSLv3 is disabled, and TLS 1.2 is enabled.
    - Path: `chef-and-ansible/tests/website_https_verify.rb`
    - Technology: Chef InSpec
    - Key Features: port and HTTP checks, protocol validation, TLS acceptance criteria.

- **ssh_root_login_compliance**:
    - Description: Chef InSpec control asserting that SSH root login is not permitted, with a fallback condition for systems without the OpenSSH server package.
    - Path: `chef-and-ansible/tests/ssh_profile.rb`
    - Technology: Chef InSpec
    - Key Features: `sshd_config` validation, package-state check, security control metadata and severity.

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, Ubuntu 20.04, the Ansible provisioner, and InSpec verification. It is the primary integration-test harness; migrate or replace it with an Ansible-native CI workflow if Test Kitchen is being retired.
- `chef-and-ansible/README.md`: Describes the examples as Ansible plus Chef InSpec compliance demonstrations. Preserve the compliance intent while updating operational instructions.
- `README.md`: Repository-level description of Chef examples and their publishing context.
- `chef-and-ansible/index.html`: Example web content; not an infrastructure module, but it is a deployment fixture.
- `setup-automate/deploy-automate.sh`: Chef platform installation infrastructure and a source of operational dependencies.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server-only installation infrastructure.

### Target Details

- **Operating System:** The tested target is Ubuntu 20.04, inferred explicitly from `kitchen.yml`; the playbooks use Debian/Ubuntu `apt`, `/etc/apache2`, `a2ensite`, and `a2enmod`. The InSpec SSH control contains a RHEL 8 STIG reference, but that is compliance metadata rather than evidence that the playbooks target RHEL. Validate whether Ubuntu 20.04 remains supported; it should not be assumed for new deployments.
- **Virtual Machine Technology:** Vagrant is specified as the Test Kitchen driver. The deployment scripts otherwise describe an on-premises or cloud VM without identifying a production hypervisor.
- **Cloud Platform:** Not specified. The Chef bootstrap scripts support generic on-premises or cloud VMs and do not identify AWS, Azure, or GCP.

## Migration Approach

### Key Dependencies to Address

- **Ansible and `ansible.builtin` modules:** Standardize module FQCNs. Existing playbooks mix short module names (`apt`, `file`, `copy`, `command`, `replace`) with `ansible.builtin.service`; convert all modules to FQCNs and pin a tested `ansible-core` version.
- **Ubuntu 20.04 and Apache 2.4.41-4ubuntu3.10:** The package is hard-pinned and may no longer be available or appropriate. Parameterize the version, define supported OS versions, and test repository availability before migration.
- **`community.crypto`/OpenSSL functionality:** The `openssl_privatekey`, `openssl_csr`, and `openssl_certificate` tasks require the appropriate Ansible collection/version. Pin the collection and decide whether self-signed certificates are acceptable outside testing.
- **Apache utilities and service names:** `a2dissite` and `a2ensite` are Debian-family commands; replace shell/command usage with idempotent Apache modules or carefully guarded commands where suitable. Confirm the SSH service name (`sshd` versus `ssh`) on Ubuntu.
- **Chef InSpec:** Retain it as an independent compliance verifier or translate the controls to Ansible Validation/ Molecule, OpenSCAP, or another approved compliance framework. The existing tests are valuable acceptance criteria, not Chef cookbook dependencies.
- **Chef Automate/Infra Server CLI:** The Bash scripts download the latest CLI from a floating URL and deploy Chef products. If Chef is being removed, replace this with an Ansible role or platform-specific provisioning workflow; if retained, manage the CLI version and bootstrap credentials securely.

### Security Considerations

- **TLS configuration:** Preserve the intent of disabling SSLv3 and enabling TLS 1.2, but assess whether TLS 1.3 should be enabled and whether current Apache/OpenSSL defaults already provide stronger behavior. Use a validated Apache configuration and test for downgrade, cipher, and certificate issues.
- **Certificate and private-key handling:** `website_https.yml` creates a private key at `/etc/apache2/certs/apache.key` and a self-signed certificate. Protect the directory and key with restrictive ownership/mode (the current directory mode `0640` is not a conventional directory mode), avoid self-signed certificates in production, and use Ansible Vault or an approved PKI for private material.
- **Hardcoded credentials:** Both Chef bootstrap scripts visibly contain a plaintext `userpassword`, usernames, email, organization names, and hostnames. Remove these values from source, use Vault/external secret management, rotate any credentials that may have been used, and avoid exposing values in process arguments or logs.
- **Generated PEM credentials:** Chef user and organization validator keys are written to local files by `chef-server-ctl`. Define secure storage, permissions, transfer, rotation, and revocation procedures; do not commit generated PEM files.
- **Privilege and SSH:** The playbooks run as `root` and use `become: yes`. Replace direct root access with an explicit deployment user and controlled privilege escalation. The InSpec SSH control should be implemented as an Ansible hardening control, with careful validation before restarting SSH to avoid lockout.
- **Supply-chain and transport security:** The scripts pipe a download from a `current/latest` URL directly into `gunzip`. Pin a release, verify checksum/signature, use HTTPS with validation, and stage the artifact through an approved repository.
- **Web content and configuration:** The embedded virtual host and HTML are fixtures. Move them into templates/files, validate Apache configuration before reload, and ensure certificate/key paths are not writable by the web service.

### Technical Challenges

- **There are no Chef cookbooks to convert:** The requested cookbook inventory is empty. The migration team must confirm whether omitted cookbooks live in another repository or whether this example repository is the complete scope.
- **Playbook idempotence and correctness:** `command` tasks for `a2ensite`, `a2dissite`, and `a2enmod` may report changes repeatedly or fail on already-applied state. Add explicit change detection, use handlers, and run `ansible-lint` and repeated convergence tests.
- **Handler name mismatch:** `poodle_fix.yml` notifies `Restart apache2`, while the declared handler is `Restart apache`; this can cause a missing-handler failure. Correct and standardize handler names before production use.
- **Apache/SSH restart coupling:** TLS changes notify SSH even though Apache SSL changes do not inherently require an SSH restart. Remove unnecessary SSH restarts and validate service impact.
- **Configuration quality:** The virtual host content contains a malformed-looking closing title tag (`</head>` is represented as `/head>`), and Apache directives should be validated with `apachectl configtest` before reload.
- **Cross-platform ambiguity:** The compliance control references RHEL 8 while the provisioning targets Ubuntu 20.04. Separate platform-specific roles or controls and define the supported matrix.
- **Testing harness modernization:** Test Kitchen/Vagrant may be difficult to maintain. Build CI around Molecule or ephemeral VMs/containers, retain the InSpec assertions where licensed and supported, and add syntax, lint, idempotence, and TLS tests.
- **Chef platform replacement:** Eliminating Chef Automate/Infra Server requires decisions about node inventory, policy enforcement, compliance reporting, user/org administration, and credential distribution—not just YAML conversion.

### Migration Order

1. **Baseline and scope confirmation:** Verify that no external Chef cookbooks or production configuration repositories are missing; inventory target OSes and decide whether Chef Automate/Infra Server remains in scope.
2. **Normalize `website_https.yml`:** Convert to an Ansible role/playbook, parameterize package/version, certificate mode and hostname, move content into templates/files, and fix Apache enablement and service handlers.
3. **Normalize `poodle_fix.yml`:** Correct the handler mismatch, make the replacement idempotent, validate Apache syntax, and integrate TLS policy with the website role rather than maintaining conflicting standalone behavior.
4. **Port compliance acceptance tests:** Keep the website HTTPS and SSH controls as CI gates, or translate them to the selected Ansible compliance framework. Test both Ubuntu and any confirmed RHEL target.
5. **Secure platform bootstrap:** If Chef remains, harden and version the bootstrap scripts. If Chef is being retired, design and implement the replacement control plane, secrets workflow, and compliance reporting separately.
6. **Production rollout:** Pilot on disposable VMs, then one non-production service, followed by staged production deployment with rollback and SSH lockout safeguards.

### Assumptions

- The supplied tree is complete; no external `cookbooks/` directory, Chef repository, Berksfile, Policyfile, or cookbook metadata is part of this migration scope.
- `website_https.yml` and `poodle_fix.yml` are the authoritative configuration sources.
- Ubuntu 20.04 is the intended example target because it is the only explicit platform in `kitchen.yml`; production OS requirements remain unconfirmed.
- Vagrant is used for testing, not necessarily production.
- The self-signed certificate is suitable only for demonstration/testing unless stakeholders approve otherwise.
- The plaintext Chef password shown in the scripts is example data, but it must still be treated as compromised if it was ever used.
- The desired end state may retain Chef InSpec for verification even if provisioning is standardized on Ansible; this requires an explicit licensing and tooling decision.
- No cloud provider, DNS, load balancer, external PKI, secret manager, inventory source, or production Apache topology is specified.
- The web application is only the embedded Hello World fixture; no application build or release pipeline is included.
- Timeline estimates exclude discovery of missing repositories, production change management, security approval, and a full replacement of Chef Automate capabilities.

## Coordination Guidance

Assign separate owners for Ansible role refactoring, security/PKI, compliance control translation, and Chef platform disposition. Establish a shared supported-OS matrix and acceptance checklist before implementation. Require peer review for all certificate, SSH, credential, and service-restart changes. Use CI to run YAML syntax checks, `ansible-lint`, repeat-convergence tests, Apache config validation, TLS protocol checks, and the SSH compliance control. Record the decision to retain or retire Chef Automate/Infra Server, document secret ownership and rotation, and perform a staged handoff with runbooks and rollback procedures.
