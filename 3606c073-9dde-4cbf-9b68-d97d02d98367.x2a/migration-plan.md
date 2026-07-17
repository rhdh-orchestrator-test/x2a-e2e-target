# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository demonstrates the integration of Chef InSpec with Ansible for compliance automation, along with scripts for deploying Chef Automate and Chef Infra Server. The migration scope is focused on standardizing on Ansible while preserving compliance testing capabilities. The estimated timeline is 1-2 weeks for a single engineer due to the relatively small codebase and low complexity.

## Module Migration Plan

This repository contains the following components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration example of Chef InSpec with Ansible for compliance testing of a web server with HTTPS configuration and security hardening
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL/TLS configuration, InSpec compliance testing, Test Kitchen integration

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server with user and organization management
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation, system configuration

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations: Replace with Molecule for Ansible-native testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server. Migration considerations: Review and refactor to follow Ansible best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Migration considerations: Integrate into the main web server playbook.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations: Preserve and integrate with Ansible testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations: Preserve and integrate with Ansible testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations: Convert to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations: Convert to an Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with one of the following Ansible solutions:
  - Option 1: Maintain InSpec and integrate with Ansible using the `ansible.builtin.shell` module
  - Option 2: Migrate to Ansible's `assert` module for basic compliance checks
  - Option 3: Implement OpenSCAP with Ansible for more comprehensive compliance testing

- **Test Kitchen (latest)**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server (latest)**: Replace with Ansible AWX/Tower for infrastructure management and compliance reporting

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the secure TLS 1.2 configuration and disable insecure protocols (SSL3) as demonstrated in the poodle_fix.yml playbook.
  Migration approach: Create an Ansible role for SSL/TLS hardening that implements the same security controls.

- **SSH Security**: The SSH compliance profile (ssh_profile.rb) checks for root login restrictions.
  Migration approach: Implement as an Ansible task and verify with appropriate tests.

- **Vault/secrets management**: For each module, credential patterns identified:
  - **setup-automate**: Hardcoded credentials in bash scripts (username, password) - 2 credentials
  - **chef-and-ansible**: SSL certificates and keys generated during playbook execution - 1 credential
  Migration approach: Move all credentials to Ansible Vault and implement secure certificate management

### Technical Challenges

- **Challenge 1: InSpec Integration**: Determining the best approach to integrate InSpec tests with Ansible or migrate to Ansible-native testing solutions while maintaining the same level of compliance verification.
  Mitigation strategy: Create a wrapper role that can execute InSpec tests as part of Ansible playbook runs, or investigate Ansible's built-in assertion capabilities.

- **Challenge 2: Chef Automate Replacement**: Finding equivalent functionality in Ansible AWX/Tower for the compliance reporting provided by Chef Automate.
  Mitigation strategy: Evaluate AWX/Tower reporting capabilities and potentially supplement with additional tools if needed.

- **Challenge 3: Maintaining Test Coverage**: Ensuring that the migration doesn't reduce test coverage or compliance verification capabilities.
  Mitigation strategy: Create a test coverage matrix to map existing InSpec tests to new Ansible-based tests.

### Migration Order

1. **Ansible Playbooks Review** (Low risk, high value): Review and refactor existing Ansible playbooks (website_https.yml, poodle_fix.yml) to follow best practices
2. **Chef Server Deployment Scripts** (Moderate complexity): Convert the Chef server deployment bash scripts to Ansible playbooks
3. **InSpec Tests Integration** (Moderate complexity, dependencies on items 1 and 2): Determine and implement the approach for integrating InSpec tests with Ansible

### Assumptions

1. The primary goal is to standardize on Ansible while maintaining the compliance testing capabilities currently provided by InSpec.
2. The existing Ansible playbooks are functional but may benefit from refactoring to follow best practices.
3. There is no requirement to maintain backward compatibility with Chef Infra Server or Chef Automate.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. The deployment will continue to support both on-premises and cloud environments.
6. The security requirements demonstrated in the InSpec tests (HTTPS, TLS 1.2, SSH restrictions) must be preserved in the migrated solution.
7. Test Kitchen can be replaced with Molecule or another Ansible-native testing framework.
8. The migration team has expertise in both Chef InSpec and Ansible.