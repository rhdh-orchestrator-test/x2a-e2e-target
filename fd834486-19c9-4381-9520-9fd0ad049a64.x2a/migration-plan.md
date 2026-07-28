# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance testing with Ansible. The repository is relatively small and appears to be primarily educational/demonstration content rather than a production infrastructure codebase. The migration scope is minimal, as most of the content is already in Ansible format, with Chef components primarily focused on InSpec testing and Chef Automate/Infra Server deployment scripts.

**Migration Complexity**: Low
**Timeline Estimate**: 1-2 weeks
**Primary Focus**: Converting InSpec tests to Ansible-native testing solutions

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS support
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration on the website
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file for testing website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule for testing playbooks
  - Option 2: Convert InSpec tests to Ansible assert tasks
  - Option 3: Maintain InSpec as a standalone testing tool but integrate with Ansible CI/CD

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Consider replacing with:
  - Ansible Tower/AWX for orchestration
  - Ansible Content Collections for role management
  - Git repositories for version control

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL and specifically address the POODLE vulnerability. Migration should maintain these security controls.
  - Migration approach: Preserve the SSL configuration parameters in the Ansible playbooks

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Convert InSpec test to Ansible assert task or Molecule test

- **Credentials Management**: 
  - Hardcoded credentials in deploy scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Challenge 1: InSpec Test Conversion**
  - Description: Converting InSpec tests to Ansible-native testing
  - Mitigation strategy: Use Ansible's assert module or Molecule for verification testing

- **Challenge 2: Chef Automate/Server Deployment**
  - Description: Replacing Chef Automate/Server deployment scripts with Ansible equivalents
  - Mitigation strategy: Create Ansible playbooks to deploy alternative orchestration platforms (AWX/Tower)

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
   - Review and optimize existing Ansible code
   - Update to use Ansible best practices (roles, collections)

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Medium complexity
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure test coverage is maintained

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Higher complexity
   - Create Ansible playbooks to replace Chef Automate/Server functionality
   - Implement Ansible Vault for credential management

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production infrastructure
2. The main goal is to standardize on Ansible rather than maintain a hybrid Chef/Ansible environment
3. Security testing is a priority based on the focus on compliance in the README
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No complex Chef cookbooks or recipes need migration as none were found in the repository