# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository presents a **unique migration scenario**: it is not a traditional Chef cookbook repository requiring migration to Ansible. Instead, it is an **educational/demonstration repository** that already contains Ansible playbooks designed to showcase integration between Chef InSpec (compliance testing) and Ansible (configuration management).

**Key Findings:**
- **No Chef cookbooks exist** in this repository - no recipes, metadata.rb, Berksfile, or Policyfile.rb were found
- The repository contains **2 functional Ansible playbooks** (`website_https.yml`, `poodle_fix.yml`) demonstrating Apache web server configuration and SSL/TLS hardening
- **Chef InSpec tests** are used for compliance verification of Ansible-managed infrastructure
- **Chef server deployment scripts** provide infrastructure setup automation but are not configuration management code

**Migration Complexity:** Not Applicable - this is already an Ansible-based implementation with Chef InSpec integration

**Recommended Action:** This repository should be used as a **reference implementation** for teams migrating from Chef to Ansible, demonstrating how to maintain compliance automation (Chef InSpec) while adopting Ansible for configuration management.

## Module Migration Plan

### MODULE INVENTORY

This repository does not contain any Chef cookbooks or modules requiring migration. The content is organized as follows:

**Ansible Playbooks (Already Migrated):**

- **website_https**:
    - Description: Apache 2.4.41 web server provisioning with HTTPS virtual host, self-signed SSL certificate generation (OpenSSL), and Hello World website deployment on Ubuntu 20.04
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: apt package management, OpenSSL certificate generation (private key, CSR, self-signed cert), Apache virtual host configuration, site activation/deactivation, service handlers for apache2 and sshd

- **poodle_fix**:
    - Description: SSL/TLS security hardening for Apache to remediate POODLE vulnerability by disabling SSLv3 and enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Regex-based configuration replacement in ssl.conf, service restart handlers, compliance-focused remediation

**Compliance Testing (Chef InSpec):**

- **website_https_verify**:
    - Description: Chef InSpec tests verifying port 443 listening, HTTPS endpoint response (200 OK with expected content), SSLv3 disabled, and TLSv1.2 enabled
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Purpose: Validates the configuration applied by website_https.yml playbook

- **ssh_profile**:
    - Description: Chef InSpec security control verifying SSH root login is disabled (STIG RHEL-08-000227, CAT I severity)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Purpose: Validates SSH hardening compliance per DISA STIG requirements

### Infrastructure Files

- **kitchen.yml**: Test Kitchen configuration using Vagrant driver, Ansible provisioner (latest version), and Chef InSpec verifier on Ubuntu 20.04 platform
- **index.html**: Static HTML test file for web server verification (simple "Hello, world!" page)
- **deploy-automate.sh**: Bash script deploying Chef Automate and Chef Infra Server with user/org creation, kernel parameter tuning (vm.max_map_count, vm.dirty_expire_centisecs)
- **deploy-chef-server.sh**: Bash script deploying standalone Chef Infra Server without Automate, with identical user/org provisioning

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbook package versions)
- **Virtual Machine Technology**: Vagrant (used for local testing via Test Kitchen)
- **Cloud Platform**: Not specified (infrastructure-agnostic playbooks suitable for on-premises or any cloud provider)

## Migration Approach

### Key Dependencies to Address

**No Chef dependencies to migrate** - this repository demonstrates the target state for migration:

- **Chef InSpec**: Retained as the compliance validation framework - no migration needed. InSpec is platform-agnostic and works seamlessly with Ansible
- **Test Kitchen with Ansible provisioner**: Already configured to use Ansible instead of Chef for provisioning
- **Ansible Collections**: Playbooks use built-in modules (apt, file, copy, command, replace, openssl_*) requiring no external dependencies

### Security Considerations

**Current Security Implementations (Already Using Ansible):**

- **SSL/TLS Hardening**: 
  - Self-signed certificate generation using OpenSSL modules (openssl_privatekey, openssl_csr, openssl_certificate)
  - POODLE vulnerability remediation (disabling SSLv3, enforcing TLSv1.2)
  - Compliance validation via InSpec ssl() resource
  - **Migration approach**: No migration needed - secure by design

- **SSH Hardening**: 
  - InSpec test validates PermitRootLogin is disabled (STIG compliance)
  - **Migration approach**: No migration needed - compliance checks remain functional

- **Secrets Management**: 
  - Hardcoded credentials in deploy scripts (userpassword='password')
  - Self-signed certificates generated dynamically (no pre-existing secrets)
  - **Recommendation**: For production use, integrate Ansible Vault for sensitive variables and consider Let's Encrypt instead of self-signed certificates

- **File Permissions**: 
  - Proper permission management (certs directory 0640, private keys protected, web content 0644)
  - **Migration approach**: No migration needed - follows security best practices

### Technical Challenges

**No migration challenges** - this is a reference implementation demonstrating successful integration. However, teams using this as a model should be aware of:

- **Test Kitchen Integration**: The kitchen.yml successfully integrates Ansible provisioner with Chef InSpec verifier - this pattern should be adopted during Chef-to-Ansible migrations to maintain compliance testing
  - Mitigation: Document this integration pattern for teams unfamiliar with Test Kitchen's multi-tool support

- **InSpec Test Maintenance**: SSH and HTTPS compliance tests are written in InSpec Ruby DSL and should be preserved during migrations
  - Mitigation: Train Ansible teams on InSpec test authoring or integrate with Ansible's built-in testing (molecule, testinfra) as a future enhancement

- **Chef Server Dependencies**: Deployment scripts install Chef Infra Server, which may not be needed post-migration
  - Mitigation: Evaluate whether Chef Server is required for InSpec compliance scanning or if InSpec can run standalone

### Migration Order

**Not Applicable** - No migration required. However, for teams adopting this approach:

1. **Adopt Test Kitchen with Ansible provisioner** (low risk, immediate testing capability)
2. **Integrate existing InSpec compliance tests** with Ansible playbooks (moderate complexity, preserves compliance automation)
3. **Evaluate Chef Server necessity** (determine if InSpec standalone mode is sufficient or if Automate is needed for compliance reporting)

### Assumptions

1. **Purpose Clarification**: This repository is assumed to be a **demonstration/training resource** for Chef InSpec + Ansible integration, not a production Chef cookbook repository requiring migration. The absence of any Chef cookbooks, recipes, or metadata files supports this assumption.

2. **Chef Server Usage**: The deploy-automate.sh and deploy-chef-server.sh scripts suggest Chef Automate may be used for **compliance reporting and visualization** of InSpec scan results, not for managing Chef cookbooks. This assumption should be validated with stakeholders.

3. **Test Kitchen Context**: The kitchen.yml configuration with `require_chef_for_busser: false` and `provisioner.name: ansible_playbook` confirms this is intentionally using Ansible for provisioning, not Chef. This is the **target state** other teams should migrate toward.

4. **Production Readiness**: The playbooks contain hardcoded values (specific Apache version 2.4.41-4ubuntu3.10, inline SSL configuration) that may need to be parameterized for production use. It's assumed these are intentionally simplified for educational purposes.

5. **InSpec Standalone Capability**: It's assumed Chef InSpec can run independently for compliance scanning without requiring Chef Infra Client or Chef Server, though the deployment scripts suggest Automate may be used for centralized reporting.

6. **Repository Evolution**: The repository may have previously contained Chef cookbooks that were migrated to Ansible, with only the deployment scripts and integration examples remaining. Historical commit analysis would clarify this assumption.

7. **Scope of "Migration"**: If the actual requirement is to **replace the Chef Server deployment scripts** with Ansible playbooks, that would be a different migration scope focused on infrastructure-as-code for Chef Automate deployment, not configuration management migration.

## Recommendations for Stakeholders

### If This Is a Reference Implementation (Most Likely)
- **Leverage as Training Material**: Use this repository to educate teams on Chef-to-Ansible migration patterns while retaining InSpec compliance
- **Expand Examples**: Add more complex scenarios (database servers, multi-tier applications) following the established pattern
- **Document Integration**: Create comprehensive documentation explaining the Test Kitchen + Ansible + InSpec workflow

### If Chef Server Deployment Needs Migration
- **Convert Deployment Scripts to Ansible**: Migrate deploy-automate.sh and deploy-chef-server.sh into Ansible playbooks using shell/command modules initially, then refactor to use package and service modules
- **Parameterize Configuration**: Replace hardcoded variables with Ansible inventory variables and Vault-encrypted secrets
- **Idempotency**: Ensure deployments are idempotent (currently scripts are not)

### If Undiscovered Chef Content Exists
- **Repository Scan**: Conduct a comprehensive scan for Chef content in other branches, tags, or external repositories referenced by this codebase
- **Clarify Scope**: Confirm with repository owners whether migration requirements apply to this specific repository or to a broader Chef infrastructure

## Conclusion

This repository represents a **successful implementation** of the migration pattern teams should adopt: using Ansible for configuration management while retaining Chef InSpec for compliance validation. No further migration work is required unless the Chef Server deployment scripts need to be converted to Ansible playbooks, which would be a separate, straightforward migration effort.
