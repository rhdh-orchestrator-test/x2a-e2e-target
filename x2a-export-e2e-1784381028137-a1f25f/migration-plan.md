# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. Chef InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef InSpec testing framework with Ansible-native testing solutions and migrating the Chef server deployment scripts to Ansible playbooks.

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible/Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Can be directly reused in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration. Can be directly reused in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration. Needs to be replaced with Ansible-native testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH compliance verification. Needs to be replaced with Ansible-native testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be replaced with an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be replaced with an Ansible playbook.

### Target Details

- **Operating System**: Ubuntu 20.04 (based on kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like:
  - Ansible Lint for static code analysis
  - Molecule for integration testing
  - ansible-test for unit testing
  - Consider OpenSCAP or DISA STIG Ansible roles for compliance testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management platforms

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening practices in the current playbooks
  - Ensure TLSv1.2 is enforced and SSLv3 is disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: Maintain compliance with SSH security controls as defined in the InSpec tests
  - Ensure root login remains disabled
  - Preserve audit trail capabilities

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys
  - Count of credentials detected:
    - setup-automate/deploy-automate.sh: 3 credentials (username, password, email)
    - setup-automate/deploy-chef-server.sh: 3 credentials (username, password, email)

### Technical Challenges

- **Compliance Testing**: Replacing Chef InSpec with Ansible-native testing solutions while maintaining the same level of compliance verification
  - Mitigation: Research and implement equivalent tests using Ansible modules or community collections
  - For SSH compliance tests, consider using ansible.posix.sshd module with appropriate parameters

- **Chef Server Replacement**: Determining the appropriate Ansible management platform to replace Chef Automate/Infra Server
  - Mitigation: Evaluate AWX/Tower or other Ansible management platforms based on organizational needs

- **SSL Certificate Management**: Ensuring secure generation and management of SSL certificates
  - Mitigation: Use Ansible's crypto modules (openssl_*) which are already in use in the current playbooks

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **Testing Framework** (Moderate complexity)
   - Replace InSpec tests with Ansible-native testing solutions
   - Update CI/CD pipelines to use new testing framework

3. **Chef Server Deployment** (High complexity)
   - Create Ansible playbooks to replace the Chef server deployment scripts
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The current setup uses Chef primarily for compliance testing (InSpec) and server deployment, while actual configuration management is already handled by Ansible.

2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.

3. Vagrant will continue to be used for development and testing environments.

4. The organization requires a centralized management platform similar to Chef Automate/Infra Server.

5. The security compliance requirements will remain the same after migration.

6. The Apache HTTPS configuration requirements will remain unchanged.

7. The migration will not involve significant changes to the application architecture or deployment strategy.