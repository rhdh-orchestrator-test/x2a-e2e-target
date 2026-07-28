# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a standardized Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance validation
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef Automate/Infra Server deployment scripts with Ansible playbooks.

Estimated timeline: 1-2 weeks for a complete migration, with the majority of time spent on creating equivalent testing capabilities in Ansible.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook for configuring Apache with HTTPS support, including certificate generation and virtual host configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Self-signed SSL certificate generation, Apache virtual host configuration, website deployment

- **poodle-fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, configures TLSv1.2, restarts affected services

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Should be converted to equivalent Ansible tests.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance profile for SSH security. Should be converted to Ansible security role with integrated tests.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - For functional testing: Replace with Molecule for Ansible role testing
  - For compliance testing: Consider using ansible-lint with custom rules or OpenSCAP with Ansible integration

- **Test Kitchen**: Replace with Molecule for Ansible role testing, which provides similar functionality but is designed for Ansible

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Set up equivalent centralized configuration management
  - Consider AWX/Ansible Tower for web UI and API functionality
  - Implement GitOps workflow with CI/CD integration

### Security Considerations

- **SSL Configuration**: The existing playbooks properly configure TLSv1.2 and disable vulnerable protocols. Migration should maintain or enhance these security practices.
  - Migration approach: Preserve the existing SSL hardening configurations in the Ansible roles

- **SSH Hardening**: The InSpec profile checks for secure SSH configuration. Migration should include an Ansible role that implements these same security controls.
  - Migration approach: Create an Ansible role that configures SSH according to the compliance requirements in the InSpec profile

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys
  - Document the count and type of credentials detected per module:
    - chef-automate-deploy: 1 password (hardcoded)
    - chef-server-deploy: 1 password (hardcoded)

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of test assertions.
  - Mitigation strategy: Create a mapping document between InSpec resources and equivalent Ansible modules/assertions

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible-native alternatives.
  - Mitigation strategy: Evaluate AWX/Tower for UI/API needs and implement GitOps workflow with CI/CD for configuration management

- **Compliance Automation**: Maintaining compliance automation capabilities without InSpec.
  - Mitigation strategy: Implement compliance-as-code using Ansible roles with integrated tests that verify the same controls

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
   - Create proper Ansible role structure
   - Add documentation
   - Set up Molecule testing

2. **poodle-fix playbook** (low risk, already in Ansible format)
   - Convert to Ansible role
   - Add documentation
   - Set up Molecule testing

3. **InSpec tests** (moderate complexity)
   - Convert website_https_verify.rb to Molecule tests
   - Convert ssh_profile.rb to Ansible role with integrated tests

4. **Chef deployment scripts** (high complexity)
   - Create Ansible playbooks for equivalent functionality
   - Implement secure credential management with Ansible Vault
   - Document alternative approaches (AWX/Tower)

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The hardcoded credentials in the deployment scripts are examples and not used in production.
3. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
4. The repository is intended for educational/demonstration purposes based on the README content.
5. There is no complex state management or data persistence that needs to be preserved during migration.
6. The Chef InSpec tests are used for validation and compliance checking rather than for continuous compliance monitoring.
7. The deployment scripts are used for setting up test environments rather than production systems.