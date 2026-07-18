# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec testing integration
3. Test profiles for compliance validation

The migration complexity is relatively low as most of the Ansible components are already in place and the Chef components are primarily deployment scripts rather than complex cookbooks. The estimated timeline for migration is 1-2 weeks, focusing on replacing the Chef Automate/Infra Server deployment with Ansible AWX/Tower deployment and ensuring the InSpec tests are properly integrated with Ansible.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec integration for compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS deployment, SSL configuration, compliance testing with InSpec

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Continue using InSpec but integrate with Ansible using the `inspec` Ansible module
  - Option 2: Replace InSpec tests with Ansible's built-in `assert` module or Molecule testing framework
  - Option 3: Use community.general.assert module for compliance testing

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - AWX/Tower for orchestration and testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for orchestration, inventory management, and role-based access control
  - GitLab/GitHub for version control and CI/CD pipelines

### Security Considerations

- **SSL Configuration**: The `poodle_fix.yml` playbook addresses SSL POODLE vulnerability by enforcing TLSv1.2. This should be incorporated into the main Apache deployment playbook.
  
- **SSH Security**: The `ssh_profile.rb` InSpec test checks for SSH root login being disabled. This should be converted to an Ansible task that ensures SSH root login is disabled.

- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username: jtonello, password: password)
  - Self-signed SSL certificates in `website_https.yml`
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: Ensuring that compliance testing is maintained during the migration. Ansible has less mature compliance testing capabilities compared to InSpec.
  - Mitigation: Either maintain InSpec and integrate with Ansible or develop equivalent testing using Ansible's assert module and Molecule.

- **Chef Automate Functionality**: Replacing Chef Automate's compliance and reporting features with equivalent Ansible solutions.
  - Mitigation: Implement AWX/Tower for orchestration and reporting, and integrate with additional tools like Prometheus/Grafana for monitoring.

### Migration Order

1. **Ansible Playbooks** (Low risk, already Ansible): Refine existing playbooks to follow best practices
   - Combine `website_https.yml` and `poodle_fix.yml` into a single role
   - Implement Ansible Vault for any secrets

2. **InSpec Tests** (Moderate complexity): Convert to Ansible-compatible testing
   - Option 1: Maintain InSpec tests but integrate with Ansible
   - Option 2: Convert to Ansible assert or Molecule tests

3. **Chef Deployment Scripts** (High complexity): Replace with Ansible AWX/Tower deployment
   - Create Ansible playbooks to deploy AWX/Tower
   - Implement user and organization management in AWX/Tower

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec integration with Ansible rather than being a production deployment.
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a test environment.
3. The hardcoded credentials in the deployment scripts are not used in production environments.
4. The self-signed certificates in the Ansible playbooks are for testing purposes only.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs.
6. There are no additional Chef cookbooks or complex Chef recipes that need migration beyond what's visible in the repository.
7. The migration will maintain the same level of compliance testing currently provided by InSpec.