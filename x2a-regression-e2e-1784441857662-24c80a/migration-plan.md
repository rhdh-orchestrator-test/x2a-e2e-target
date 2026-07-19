# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components that need to be consolidated into a pure Ansible solution. The estimated timeline is 1-2 weeks.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with Chef InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL certificate generation, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS website. Can be directly reused in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be directly reused in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs to be replaced with Ansible testing solutions.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs to be replaced with Ansible testing solutions.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Implement Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static code analysis
  - Option 4: Integrate with other testing frameworks like Serverspec or Testinfra

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management solutions

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security practice should be maintained in the migrated Ansible solution.
  
- **SSH Security**: The InSpec tests verify SSH root login is disabled. This security check should be implemented in the Ansible solution.

- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider implementing proper certificate management in the migrated solution.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in setup scripts

### Technical Challenges

- **Testing Framework Migration**: Replacing Chef InSpec with Ansible-native testing solutions is the main technical challenge. InSpec provides specific security and compliance testing capabilities that need to be replicated.
  - Mitigation: Research and implement a combination of Ansible assert, Molecule, and possibly additional testing frameworks to achieve equivalent test coverage.

- **Chef Automate Functionality**: If Chef Automate is being used for compliance reporting and visualization, equivalent functionality needs to be implemented in the Ansible ecosystem.
  - Mitigation: Consider implementing Ansible AWX/Tower with custom reporting or integrating with compliance tools like OpenSCAP.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml)
   - Low risk as they are already Ansible playbooks
   - Focus on replacing InSpec testing with Ansible-native testing

2. **Chef Deployment Scripts** (setup-automate/deploy-chef-server.sh, setup-automate/deploy-automate.sh)
   - Medium complexity
   - Convert to Ansible playbooks that either deploy alternative solutions or deploy Chef if still required

### Assumptions

1. The primary goal is to consolidate on Ansible and eliminate Chef dependencies where possible.
2. The InSpec tests are essential for compliance and security validation and equivalent functionality must be maintained.
3. The deployment scripts for Chef Automate/Infra Server are being migrated because Chef infrastructure itself is being replaced with Ansible AWX/Tower or similar.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. Vagrant will continue to be used for development/testing environments.
6. The security requirements (TLS 1.2, SSH hardening) must be maintained in the migrated solution.
7. The current implementation does not use complex Chef-specific features that would be difficult to replicate in Ansible.