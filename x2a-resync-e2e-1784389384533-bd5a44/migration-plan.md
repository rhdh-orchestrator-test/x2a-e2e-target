# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Chef InSpec test profiles used alongside Ansible playbooks for compliance testing
2. Ansible playbooks for configuring web servers with HTTPS
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **MEDIUM** with an estimated timeline of 2-3 weeks. The primary focus will be on:
- Converting Chef InSpec tests to Ansible-compatible testing frameworks
- Enhancing existing Ansible playbooks for better maintainability
- Replacing Chef Automate/Infra Server deployment scripts with Ansible equivalents

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Mixed (Ansible playbooks with Chef InSpec tests)
    - Key Features: HTTPS website deployment, SSL/TLS configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef server deployment, user/organization creation, system configuration

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website. Can be retained but should be refactored into roles.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL security fixes. Can be retained but should be integrated into a security role.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website. Should be converted to Ansible-compatible test framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be converted to Ansible-compatible test framework.
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate deployment. Should be replaced with Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for Chef Server deployment. Should be replaced with Ansible playbook or removed if Chef Server is no longer needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible's `assert` module for basic testing
  - Option 2: Molecule for comprehensive testing
  - Option 3: Integration with other testing frameworks like Serverspec or TestInfra

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Determine if these are still needed or can be replaced with:
  - Ansible Tower/AWX for orchestration
  - GitLab CI/GitHub Actions for pipeline execution
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security roles

### Security Considerations

- **SSL/TLS Configuration**: The current implementation sets up TLS 1.2 and disables older protocols. Migration should:
  - Update to include TLS 1.3 support
  - Implement modern cipher suites
  - Add HSTS headers

- **SSH Hardening**: Current InSpec tests verify SSH root login is disabled. Migration should:
  - Implement SSH hardening via Ansible security roles
  - Maintain compliance testing for SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate generation should use Ansible Vault for key storage or integrate with external certificate management

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to Ansible-native testing requires:
  - Mapping InSpec resources to Ansible modules
  - Ensuring equivalent coverage of compliance checks
  - Maintaining test readability and maintainability

- **Chef Server Replacement**: If Chef Server is being used for configuration management:
  - Inventory management needs to be migrated to Ansible inventory
  - Node attributes need to be converted to Ansible variables
  - Cookbook logic needs to be reimplemented as Ansible roles

- **Compliance Reporting**: If Chef Automate is being used for compliance reporting:
  - Need to implement alternative compliance reporting solution
  - Options include OpenSCAP, Ansible Tower/AWX, or third-party tools

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Refactor `website_https.yml` and `poodle_fix.yml` into proper Ansible roles
   - Implement variable management and improve modularity

2. **Testing Framework** (Medium complexity)
   - Convert InSpec tests to Ansible-compatible testing framework
   - Implement test automation with Molecule or similar tool

3. **Chef Automate/Server Deployment** (High complexity)
   - Determine if Chef components are still needed
   - If not, replace with Ansible Tower/AWX or similar orchestration
   - If still needed, create Ansible playbooks to deploy Chef infrastructure

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The Chef Automate and Chef Server deployment scripts are for setting up test environments rather than production systems.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and not used in production.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. The migration goal is to standardize on Ansible and remove Chef dependencies where possible.
6. Compliance testing is a critical requirement that must be maintained in the migrated solution.
7. The existing Ansible playbooks are functional but may benefit from refactoring into roles for better maintainability.