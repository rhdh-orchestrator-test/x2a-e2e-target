# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance verification
4. Ensuring the integration between Ansible and InSpec remains functional

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **website-https-deployment**:
    - Description: Ansible playbook for deploying a secure website with Apache, SSL certificates, and proper configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL configuration hardening, service restart

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible-native testing framework or adapt to use Molecule with InSpec verifier.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment. Migration consideration: Preserve as-is for compliance testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration consideration: Preserve as-is for compliance testing.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management platform
  - Migration strategy: Create Ansible playbooks to deploy AWX/Tower instead of Chef Automate
  - Consider using the official AWX Operator for Kubernetes if moving to a container-based approach

- **Test Kitchen**: Replace with Ansible Molecule
  - Migration strategy: Create Molecule scenarios that replicate the existing Test Kitchen functionality
  - Ensure Molecule is configured to use InSpec as a verifier to maintain compliance testing

- **InSpec**: Maintain as compliance testing framework
  - Migration strategy: Keep InSpec tests as-is, integrate with Ansible using the `ansible.builtin.shell` module to run InSpec tests
  - Consider implementing an Ansible role that installs and runs InSpec tests

### Security Considerations

- **SSL/TLS Configuration**: The existing Ansible playbooks properly configure TLS 1.2 and disable insecure protocols. This should be maintained in the migrated solution.
  - Migration approach: Preserve the existing SSL hardening configurations in the Ansible playbooks

- **SSH Hardening**: The repository includes InSpec tests for SSH security compliance.
  - Migration approach: Maintain the InSpec tests and create an Ansible role for SSH hardening that satisfies these tests

- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate to Ansible AWX/Tower Migration**: Converting the Chef Automate deployment to an equivalent Ansible management platform will require careful planning.
  - Mitigation strategy: Research AWX/Tower deployment options, create a phased migration plan, and ensure feature parity for user management and organization structure

- **InSpec Integration**: Ensuring InSpec tests continue to work seamlessly with Ansible.
  - Mitigation strategy: Create a dedicated Ansible role for running InSpec tests, with proper error handling and reporting

- **Compliance Reporting**: Maintaining compliance reporting capabilities when moving from Chef Automate to Ansible.
  - Mitigation strategy: Investigate compliance reporting options in Ansible AWX/Tower or consider additional tools like Prometheus/Grafana for visualization

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Preserve existing playbooks (website_https.yml, poodle_fix.yml)
   - Update any deprecated syntax or modules
   - Implement Ansible Vault for any sensitive data

2. **InSpec Tests** (Low risk, maintain as-is)
   - Create an Ansible role for running InSpec tests
   - Ensure proper integration with existing playbooks

3. **Chef Automate/Infra Server Deployment** (High complexity)
   - Create Ansible playbooks to replace the bash scripts
   - Implement secure credential management with Ansible Vault
   - Test thoroughly to ensure equivalent functionality

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool while maintaining compliance testing with InSpec.
2. The existing Ansible playbooks are functional and follow best practices.
3. The Chef Automate/Infra Server deployment scripts are used for setting up the management platform, not for actual configuration management.
4. The InSpec tests are valuable and should be preserved for compliance verification.
5. No actual Chef cookbooks or recipes are present in the repository, only deployment scripts for Chef Automate/Infra Server.
6. The target environment will continue to be Ubuntu 20.04 or compatible systems.
7. Vagrant will continue to be used for development/testing environments.