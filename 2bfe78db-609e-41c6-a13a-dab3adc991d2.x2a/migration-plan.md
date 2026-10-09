# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance testing examples integrated with Ansible playbooks, rather than traditional Chef cookbooks. The migration scope is minimal as the infrastructure automation is already implemented in Ansible - the primary task is to replace Chef InSpec testing with native Ansible testing approaches. Timeline estimate: 1-2 weeks for a small team to migrate testing frameworks and update CI/CD pipelines.

## Module Migration Plan

This repository contains Chef InSpec compliance tests and Ansible playbooks that demonstrate compliance automation integration:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths verified from the provided repository tree structure.

- **website-https-compliance**:
    - Description: Apache HTTPS website deployment with SSL/TLS configuration and compliance verification using Chef InSpec
    - Path: chef-and-ansible/
    - Technology: Ansible playbooks with Chef InSpec testing
    - Key Features: Self-signed SSL certificate generation, Apache virtual host configuration, HTTPS compliance testing, SSL protocol enforcement (TLS 1.2 only)

- **ssh-security-compliance**:
    - Description: SSH security hardening compliance tests following STIG requirements for root login restrictions
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, STIG compliance checks (SRG-OS-000112, V-38607), security control validation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification - needs migration to molecule or native Ansible testing
- `website_https.yml`: Ansible playbook for Apache HTTPS setup - already in target format, no migration needed
- `poodle_fix.yml`: Ansible playbook for SSL POODLE vulnerability remediation - already in target format, no migration needed
- `deploy-automate.sh`: Chef Automate server deployment script - can be retired or converted to Ansible playbook
- `deploy-chef-server.sh`: Chef Infra Server deployment script - can be retired or converted to Ansible playbook

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml driver)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible native testing using ansible-test, molecule, or testinfra
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and verification
- **Chef Automate/Server**: Remove dependency on Chef infrastructure components

### Security Considerations
- SSL/TLS certificate management: Current implementation uses self-signed certificates generated via OpenSSL Ansible modules - no migration needed
- SSH hardening compliance: Migrate InSpec controls to Ansible assert tasks or molecule verifiers
- STIG compliance verification: Replace Chef InSpec STIG profiles with Ansible security role validation
- Credential management: No hardcoded credentials found in playbooks - uses Ansible variables appropriately

### Technical Challenges
- **InSpec to Ansible Testing Migration**: Converting Chef InSpec compliance tests to native Ansible verification methods requires rewriting test logic
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires updating CI/CD pipelines and test execution workflows  
- **Compliance Framework Integration**: Maintaining STIG compliance verification without Chef InSpec may require additional tooling or custom Ansible modules
- **SSL Protocol Testing**: Current InSpec tests verify SSL protocol configurations - need equivalent Ansible testing approach

### Migration Order
1. **Ansible Playbooks** (already complete - no migration needed)
2. **Test Framework Migration** (replace Test Kitchen with Molecule)
3. **Compliance Test Migration** (convert InSpec tests to Ansible native testing)
4. **CI/CD Pipeline Updates** (update automation workflows to use new testing framework)

### Assumptions
- The target environment will continue using Ansible for infrastructure automation (no Chef cookbooks to migrate)
- Compliance testing requirements remain the same but can be implemented using Ansible native testing tools
- Test Kitchen and Chef InSpec dependencies can be completely removed from the testing pipeline
- The demonstration/example nature of this repository means production deployment considerations may not be fully represented
- SSL certificate management will continue using Ansible OpenSSL modules rather than external certificate authorities
- Ubuntu 20.04 target platform assumption based on kitchen.yml - actual production targets may differ