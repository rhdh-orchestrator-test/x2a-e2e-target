# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec testing capabilities within an Ansible-only workflow

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most infrastructure already defined in Ansible

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing but integrate with Ansible workflow
  - Replace Test Kitchen with Ansible's native molecule testing framework with InSpec verifier
  - Alternatively, call InSpec directly from Ansible playbooks using the `command` module

- **Chef Automate/Infra Server**: Replace with Ansible automation platform
  - Convert Chef Automate/Infra Server deployment scripts to Ansible roles
  - Consider using AWX/Ansible Tower as a replacement for Chef Automate's UI capabilities

### Security Considerations

- **SSL Configuration**: The existing playbooks properly configure SSL with TLSv1.2 and disable vulnerable protocols
  - Maintain this security practice in the migrated Ansible roles
  - Consider enhancing with modern TLSv1.3 support

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Ensure SSH hardening is implemented in the migrated Ansible roles
  - Add Ansible tasks to enforce SSH security configurations being tested

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically, no migration needed

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with Ansible-only workflow
  - Solution: Use Ansible's `command` module to run InSpec tests or integrate with molecule testing framework

- **Chef Server Replacement**: Determining if Chef Server functionality is needed
  - Solution: Evaluate if AWX/Ansible Tower can replace Chef Server functionality or if a simpler Git-based approach is sufficient

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Review and optimize existing Ansible code
   - Add documentation and variable customization

2. **poodle_fix playbook** (low risk, already Ansible)
   - Review and optimize existing Ansible code
   - Consider merging with website_https as an optional security enhancement

3. **Chef deployment scripts** (medium complexity)
   - Convert bash scripts to Ansible roles for deploying automation platforms
   - Replace Chef Automate/Infra Server with AWX/Ansible Tower if needed

4. **Testing Framework** (medium complexity)
   - Migrate from Test Kitchen to molecule or direct InSpec integration
   - Ensure all existing tests continue to function

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README stating it provides "working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams."

2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments rather than production infrastructure.

3. The InSpec tests are valuable and should be preserved in the migration to Ansible.

4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure values in a production environment.

5. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already well-structured and may need minimal changes.