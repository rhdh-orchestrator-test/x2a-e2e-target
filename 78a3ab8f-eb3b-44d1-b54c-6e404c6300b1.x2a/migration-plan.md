# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository is a **demonstration/example repository** that showcases the integration between Chef InSpec and Ansible for compliance automation. The repository does **NOT** contain traditional Chef cookbooks requiring migration. Instead, it contains:

1. **Already-migrated Ansible playbooks** demonstrating infrastructure automation
2. **Chef InSpec test profiles** for compliance verification (which should remain as InSpec)
3. **Chef Automate/Server deployment scripts** for setting up the Chef infrastructure platform

**Migration Scope**: Minimal - This is primarily a reference implementation showing Chef InSpec integration with Ansible. The infrastructure automation is already in Ansible format. The InSpec tests should remain as-is since Chef InSpec is the industry-standard compliance-as-code framework that integrates with Ansible.

**Complexity**: Low - No active Chef cookbooks to migrate

**Timeline Estimate**: 1-2 days for documentation updates and script refactoring only

**Recommendation**: This repository serves as a working example of the target state (Ansible + InSpec). If this is a reference repository, no migration is needed. If the deployment scripts need to be Ansibleized, that is a straightforward 1-2 day effort.

## Module Migration Plan

This repository does NOT contain Chef cookbooks or recipes. It contains example Ansible playbooks with InSpec tests.

### MODULE INVENTORY

**No Chef modules found.** The repository contains:

1. **Ansible Playbooks** (already in target format):
   - `chef-and-ansible/website_https.yml` - Apache HTTPS configuration playbook
   - `chef-and-ansible/poodle_fix.yml` - SSL/TLS hardening playbook

2. **Chef InSpec Test Profiles** (should remain as InSpec):
   - `chef-and-ansible/tests/website_https_verify.rb` - HTTPS website compliance tests
   - `chef-and-ansible/tests/ssh_profile.rb` - SSH security compliance tests

3. **Infrastructure Deployment Scripts**:
   - `setup-automate/deploy-automate.sh` - Chef Automate + Infra Server deployment
   - `setup-automate/deploy-chef-server.sh` - Chef Infra Server only deployment

### Infrastructure Files

#### Ansible Playbooks (Already Migrated)
- **`chef-and-ansible/website_https.yml`**: Complete Apache HTTPS setup playbook
  - Installs Apache 2.4.41 on Ubuntu 20.04
  - Generates self-signed SSL certificates using OpenSSL modules
  - Configures virtual host with SSL/TLS
  - Deploys "Hello World" test website
  - **Migration Status**: Already in Ansible - no action needed

- **`chef-and-ansible/poodle_fix.yml`**: SSL/TLS security hardening playbook
  - Disables SSLv3 and enforces TLSv1.2 to mitigate POODLE vulnerability
  - Updates Apache SSL configuration
  - **Migration Status**: Already in Ansible - no action needed

#### Test Kitchen Configuration
- **`chef-and-ansible/kitchen.yml`**: Test Kitchen configuration using Ansible provisioner
  - Uses Vagrant driver for local testing
  - Provisions with Ansible (not Chef)
  - Verifies with InSpec
  - Target platform: Ubuntu 20.04
  - **Migration Consideration**: This file demonstrates the target testing pattern

#### Chef InSpec Test Profiles
- **`chef-and-ansible/tests/website_https_verify.rb`**: InSpec profile for HTTPS verification
  - Verifies port 443 is listening
  - Tests HTTP 200 response and content
  - Validates SSL/TLS protocol configuration (SSLv3 disabled, TLS 1.2 enabled)
  - **Migration Status**: Keep as InSpec - this is the compliance verification layer

- **`chef-and-ansible/tests/ssh_profile.rb`**: InSpec profile for SSH security
  - Tests STIG compliance (RHEL-08-000227, CCI-000774)
  - Verifies PermitRootLogin is disabled
  - CAT I (Critical) severity control
  - **Migration Status**: Keep as InSpec - this validates security posture

#### Chef Infrastructure Deployment Scripts
- **`setup-automate/deploy-automate.sh`**: Bash script to deploy Chef Automate + Infra Server
  - Configures hostname and kernel parameters
  - Downloads and deploys chef-automate CLI
  - Creates initial user and organization
  - Hardcoded credentials (security concern)
  - **Migration Opportunity**: Convert to Ansible playbook for idempotent deployment

- **`setup-automate/deploy-chef-server.sh`**: Bash script to deploy Chef Infra Server only
  - Similar to deploy-automate.sh but without Automate component
  - Same security concerns with hardcoded credentials
  - **Migration Opportunity**: Convert to Ansible playbook for idempotent deployment

#### Static Files
- **`chef-and-ansible/index.html`**: Static HTML file for testing
  - Simple "Hello, world!" page
  - Used as test content by the playbooks

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (as specified in kitchen.yml and playbooks)
- **Virtual Machine Technology**: Vagrant (for local development/testing), can be deployed to any VM platform
- **Cloud Platform**: Cloud-agnostic - the deployment scripts reference "on-prem or cloud VM" and can target any infrastructure

## Migration Approach

### Key Dependencies to Address

**No Chef cookbook dependencies exist.** The repository uses:

- **ansible.builtin modules**: Already included in Ansible core
- **community.crypto collection** (implied by openssl_* modules): Should be explicitly declared
  - Add to `requirements.yml`:
    ```yaml
    collections:
      - name: community.crypto
        version: ">=2.0.0"
    ```
- **Chef InSpec**: Remains as the compliance testing framework (no migration needed)
- **chef-automate CLI**: Used only for Chef platform deployment (deployment scripts)

### Security Considerations

#### Credentials and Secrets Management
- **Deployment Scripts**: Hardcoded credentials in `setup-automate/*.sh` scripts
  - Username: `jtonello`
  - Email: `jtonello@chef.lab`
  - Password: `password` (plaintext)
  - Organization: `lab`
  - **Migration Approach**: If converting scripts to Ansible, use Ansible Vault for credentials:
    ```bash
    ansible-vault create group_vars/all/vault.yml
    ```
    Store encrypted variables:
    ```yaml
    vault_chef_username: jtonello
    vault_chef_password: <strong_password>
    vault_chef_email: jtonello@chef.lab
    ```

#### SSL/TLS Configuration
- **Self-Signed Certificates**: The `website_https.yml` playbook generates self-signed certificates
  - Suitable for testing/demo purposes
  - **Production Migration**: Replace with proper CA-signed certificates or Let's Encrypt integration
  - Consider using `community.crypto.acme_certificate` for Let's Encrypt automation

- **TLS Protocol Hardening**: The `poodle_fix.yml` playbook enforces TLS 1.2
  - **Recommendation**: Update to enforce TLS 1.2+ or TLS 1.3 only
  - Current configuration disables SSLv3 (good) but may need TLS 1.0/1.1 disabled for modern compliance

#### SSH Security
- **InSpec Profile**: Tests for disabled root login (STIG compliance)
  - This is a verification test, not a configuration
  - **Gap**: No Ansible playbook exists to enforce this SSH hardening
  - **Recommendation**: Create an SSH hardening playbook that the InSpec profile can verify

### Technical Challenges

#### 1. Repository Purpose Ambiguity
- **Challenge**: This is a demonstration repository showing how to use InSpec with Ansible, not a traditional Chef-to-Ansible migration candidate
- **Impact**: Low - No actual cookbook migration required
- **Mitigation**: Clarify whether this repository should be:
  - Kept as-is (reference example)
  - Enhanced with more examples
  - Used as a template for other migrations

#### 2. Test Kitchen Configuration
- **Challenge**: Test Kitchen is traditionally a Chef tool, but this config uses Ansible provisioner
- **Impact**: Low - Configuration works as-is
- **Consideration**: Teams fully migrated to Ansible might prefer:
  - Molecule (Ansible's native testing framework)
  - Pure Ansible with InSpec verifier
- **Mitigation**: Document that Test Kitchen is acceptable for mixed environments

#### 3. Deployment Script Idempotency
- **Challenge**: Bash scripts in `setup-automate/` are not idempotent
- **Impact**: Medium - Scripts will fail if run multiple times
- **Mitigation**: If converting to Ansible:
  - Check if Chef Automate is already installed before downloading
  - Use `creates` parameter for download tasks
  - Conditionally create users/orgs only if they don't exist

#### 4. InSpec Integration Pattern
- **Challenge**: Teams new to Ansible might not understand why InSpec is still used
- **Impact**: Low - Documentation gap
- **Mitigation**: Enhance README with clear explanation:
  - InSpec is the compliance-as-code standard (works with Ansible, Chef, Terraform, etc.)
  - Ansible handles configuration management
  - InSpec handles compliance verification
  - This separation of concerns is intentional and recommended

### Migration Order

Since this repository contains minimal Chef-specific content, the suggested order focuses on enhancement rather than migration:

1. **Documentation Updates** (Priority 1 - Immediate)
   - Update `README.md` to clarify this is a reference implementation
   - Document the Ansible + InSpec integration pattern
   - Add architecture diagrams showing the workflow
   - Estimated effort: 4 hours

2. **Ansible Collection Requirements** (Priority 2 - Low Risk)
   - Create `requirements.yml` for explicit dependency management
   - Add `community.crypto` collection
   - Add `ansible.posix` if SSH hardening playbook is created
   - Estimated effort: 1 hour

3. **SSH Hardening Playbook** (Priority 3 - Enhancement)
   - Create playbook to enforce SSH security settings
   - Align with the existing `ssh_profile.rb` InSpec test
   - Add to Test Kitchen suite
   - Estimated effort: 4 hours

4. **Convert Deployment Scripts to Ansible** (Priority 4 - Optional)
   - Convert `deploy-automate.sh` to Ansible playbook
   - Convert `deploy-chef-server.sh` to Ansible playbook
   - Implement Ansible Vault for credentials
   - Add idempotency checks
   - Estimated effort: 1-2 days

5. **Enhance Test Coverage** (Priority 5 - Optional)
   - Add more InSpec profiles for common compliance frameworks
   - Add corresponding Ansible remediation playbooks
   - Create end-to-end CI/CD examples
   - Estimated effort: 3-5 days

### Assumptions

1. **Repository Purpose**: Assuming this is a demonstration/reference repository for showcasing Chef InSpec integration with Ansible, not a production infrastructure repository requiring active migration.

2. **InSpec Retention**: Assuming Chef InSpec will remain as the compliance testing framework post-migration, which is standard practice. InSpec is technology-agnostic and commonly used with Ansible.

3. **Test Kitchen vs Molecule**: Assuming Test Kitchen with Ansible provisioner is acceptable. If the organization has standardized on Molecule, this would need discussion.

4. **Deployment Scripts Conversion**: The priority of converting the Chef Automate deployment scripts to Ansible is unclear. If the organization is fully migrating away from Chef infrastructure (Automate/Infra Server), these scripts may not need conversion at all.

5. **Target Audience**: Assuming this repository is used for:
   - Training and education on Ansible + InSpec integration
   - Reference implementation for other teams
   - Proof-of-concept for compliance automation patterns
   
   If the actual use case is different (e.g., production deployment automation), priorities would shift significantly.

6. **SSL Certificate Strategy**: The playbooks use self-signed certificates, which is appropriate for testing. Production requirements for certificate management (Let's Encrypt, internal CA, cert rotation) are not specified.

7. **Compliance Framework**: The SSH InSpec profile references RHEL 8 STIG controls, but the target OS is Ubuntu 20.04. Assuming this is intentional for demonstration purposes, but there may be a mismatch between the control framework and target OS.

8. **Version Requirements**: No explicit version constraints exist for Ansible or InSpec. Assuming latest stable versions are acceptable, but production use should pin specific versions in `requirements.yml` and `Gemfile`/`.tool-versions`.

9. **Playbook Scope**: The existing playbooks are minimal examples. Assuming they are intentionally simple for educational purposes, not production-ready automation requiring error handling, logging, and rollback capabilities.

10. **Chef Infrastructure Dependencies**: If the deployment scripts are relevant, assuming there is an existing need for Chef Automate/Infra Server in the environment (perhaps for managing other non-migrated systems, or for the InSpec backend). If Chef infrastructure is being completely decommissioned, these scripts are obsolete.

## Conclusion

This repository represents a **hybrid Ansible + Chef InSpec** pattern that is actually the recommended target state for compliance automation. The infrastructure configuration is already in Ansible format, and the compliance verification uses Chef InSpec, which is appropriate.

**No traditional Chef cookbook migration is required.** The primary opportunities are:

1. **Documentation enhancement** to clarify the integration pattern
2. **Optional conversion** of deployment scripts to Ansible for consistency
3. **Addition of missing hardening playbooks** to complement existing InSpec tests

This repository should be viewed as a **template or reference implementation** rather than a migration candidate.
