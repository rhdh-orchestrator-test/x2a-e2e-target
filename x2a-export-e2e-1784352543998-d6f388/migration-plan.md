# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is **LOW** as most of the content is already in Ansible format, with the primary focus being on replacing Chef InSpec with Ansible-compatible compliance testing solutions and migrating Chef server deployment scripts to Ansible playbooks. Estimated timeline: **1-2 weeks** for a complete migration.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Migration consideration: Can be kept as-is in Ansible format.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Can be kept as-is in Ansible format.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification. Migration consideration: Replace with Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration consideration: Replace with Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Replace with Ansible playbook for infrastructure deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Replace with Ansible playbook for infrastructure deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in setup-automate scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible compliance testing solutions:
  - Option 1: Use Ansible's built-in assert module for basic compliance checks
  - Option 2: Integrate with OpenSCAP for more comprehensive compliance testing
  - Option 3: Use Ansible Lint for static code analysis and best practices enforcement

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing:
  - Molecule provides similar functionality for testing Ansible roles and playbooks
  - Can use the same Vagrant driver for VM provisioning

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for playbook storage and version control
  - Consider Ansible Semaphore as a lightweight alternative

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Migration should maintain:
  - Self-signed certificate generation
  - TLS 1.2 enforcement (disabling older protocols)
  - Proper certificate file permissions

- **SSH Hardening**: The InSpec profile checks for SSH root login disablement. Migration should:
  - Incorporate SSH hardening into Ansible playbooks
  - Implement equivalent compliance checks using Ansible's assert module

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **Compliance Testing**: Replacing InSpec with Ansible-native testing solutions:
  - Challenge: InSpec provides a domain-specific language for compliance testing that is more expressive than Ansible's built-in testing capabilities
  - Mitigation: Use a combination of Ansible assert module and external tools like OpenSCAP; consider maintaining InSpec as a separate tool if needed

- **Infrastructure Deployment**: Replacing Chef server deployment scripts:
  - Challenge: The scripts install and configure Chef-specific components that won't be needed in an Ansible-only environment
  - Mitigation: Replace with Ansible AWX/Tower deployment playbooks or other CI/CD infrastructure as needed

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format):
   - `website_https.yml` and `poodle_fix.yml` can be kept as-is
   - Update any references to Chef-specific components if needed

2. **Testing Framework** (Moderate complexity):
   - Replace Test Kitchen with Molecule
   - Convert InSpec tests to Ansible assertions or OpenSCAP checks

3. **Infrastructure Deployment** (High complexity):
   - Replace Chef Automate and Chef Infra Server deployment scripts with Ansible playbooks for AWX/Tower deployment

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use, as indicated by the README.md mentioning it's a companion to a white paper.

2. The Chef InSpec tests are used for compliance verification of Ansible-managed systems, showing how Chef and Ansible can work together rather than being completely separate technologies.

3. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the scripts are designed to work in both on-premises and cloud environments.

4. There are no complex Chef cookbooks or recipes to migrate, as the repository focuses on demonstrating InSpec with Ansible rather than extensive Chef usage.

5. The hardcoded credentials in the setup scripts are for demonstration purposes and would need proper secret management in a production environment.

6. The repository does not contain any application-specific configurations beyond the basic Apache HTTPS setup.