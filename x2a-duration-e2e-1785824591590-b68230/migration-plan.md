# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Ansible playbooks with Chef InSpec tests for compliance verification
2. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with only a few playbooks and shell scripts to convert. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which are already in Ansible format) and medium complexity for the Chef Automate/Infra Server deployment scripts.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Keep InSpec but integrate with Ansible (recommended if compliance reporting is needed)

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Or continue using Test Kitchen with the Ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Ansible Automation Platform for enterprise features
  - Git repositories for Ansible content management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already implemented in poodle_fix.yml)
  - Consider adding modern cipher suite configurations
  - Implement automatic certificate renewal if moving to production

- **SSH Hardening**: The repository includes SSH security compliance tests:
  - Ensure SSH root login remains disabled in the Ansible equivalent
  - Implement the full SSH hardening profile as Ansible tasks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require:
  - Creating Ansible roles for Chef Automate installation (if still needed)
  - Or replacing Chef Automate functionality with Ansible Tower/AWX
  - Challenge: Ensuring all Chef Automate functionality has an Ansible equivalent

- **InSpec Testing**: Maintaining compliance testing capabilities:
  - Option 1: Keep InSpec and call it from Ansible
  - Option 2: Rewrite InSpec tests as Ansible assertions
  - Challenge: Ensuring the same level of compliance reporting

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and update to current Ansible best practices
   - Implement idempotency improvements if needed
   - Move any hardcoded values to variables

2. **InSpec Tests**: Moderate complexity
   - Decide on testing strategy (keep InSpec or migrate to Ansible-native)
   - Convert tests if necessary

3. **Chef Deployment Scripts**: Higher complexity
   - Create Ansible playbooks to replace the Chef Automate and Chef Infra Server deployment scripts
   - Or implement alternative solution with Ansible Tower/AWX

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible, not for production use
2. The Chef Automate and Chef Infra Server deployment is still needed in some form
3. The hardcoded credentials in the scripts are for demonstration purposes only
4. The target environment will continue to be Ubuntu 20.04 or similar
5. The SSL and SSH configurations are based on security best practices that should be maintained
6. Test Kitchen is used for development and testing, not for production deployments