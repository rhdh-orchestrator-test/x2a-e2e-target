# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository primarily contains Ansible playbooks already with Chef InSpec tests and Chef server deployment scripts.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Example of using Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec and Ansible
    - Key Features: HTTPS website deployment, SSL configuration testing, SSH security testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible and InSpec integration. Migration should replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Should be migrated to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be migrated to Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be migrated to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be migrated to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained in the migrated Ansible playbooks.
  - Migration approach: Preserve the existing SSL configuration in the Ansible playbooks.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec SSH tests to Ansible assert statements or Molecule tests.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated during playbook execution, which is a good practice to maintain

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing requires understanding the compliance requirements and implementing equivalent checks.
  - Mitigation: Map each InSpec resource to equivalent Ansible modules and assertions.

- **Chef Server Deployment**: The Chef server deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Create Ansible roles for Chef server deployment or replace with AWX/Tower deployment.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - `website_https.yml`
   - `poodle_fix.yml`

2. **InSpec Tests** (Medium complexity)
   - Convert `website_https_verify.rb` to Ansible/Molecule tests
   - Convert `ssh_profile.rb` to Ansible/Molecule tests

3. **Chef Server Deployment Scripts** (High complexity)
   - Convert `deploy-automate.sh` to Ansible playbook
   - Convert `deploy-chef-server.sh` to Ansible playbook

4. **Test Kitchen Configuration** (Medium complexity)
   - Replace `kitchen.yml` with Molecule configuration

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality.
2. The existing Ansible playbooks are working correctly and don't need functional changes.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The deployment scripts for Chef Automate/Infra Server will be replaced with equivalent Ansible automation or a different configuration management solution.
5. Test Kitchen will be replaced with Ansible Molecule or another Ansible-native testing framework.
6. The team has expertise in both Chef InSpec and Ansible to understand the compliance requirements being tested.