# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Optimizing existing Ansible playbooks
3. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible roles

The migration complexity is low to moderate, with an estimated timeline of 2-3 weeks for a single developer or 1 week for a small team. The primary challenge will be maintaining the compliance testing capabilities currently provided by Chef InSpec while moving to an Ansible-native solution.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS configuration and deploys a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec. Migration will require converting to Ansible Molecule or another Ansible-native testing framework.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test that verifies HTTPS configuration on the web server. Will need conversion to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile that checks SSH configuration for compliance with security standards. Will need conversion to Ansible-compatible testing framework.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but the deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible collections for compliance automation

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration maintains or improves the security posture:
  - Maintain TLSv1.2 requirement
  - Consider adding TLSv1.3 support
  - Ensure proper certificate management

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Ensure this compliance check is maintained in the Ansible solution.

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault or integration with a secrets management solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks while maintaining the same level of compliance validation
  - Mitigation: Use Ansible's assert module combined with command/shell modules to replicate InSpec tests, or consider integrating with tools like Molecule

- **Chef Automate Functionality**: Replacing Chef Automate's compliance scanning and reporting capabilities
  - Mitigation: Implement OpenSCAP with Ansible for compliance scanning, use AWX/Tower for reporting

- **Deployment Scripts**: Converting the Chef Automate and Chef Infra Server deployment scripts to Ansible roles
  - Mitigation: Create Ansible roles that perform the same system configuration and application deployment steps

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need optimization and best practices applied
2. **Testing Framework**: Convert InSpec tests to Ansible-compatible testing framework
3. **Deployment Scripts**: Convert Chef Automate and Chef Infra Server deployment scripts to Ansible roles

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible for compliance automation, not for production deployment
2. The hardcoded credentials in the deployment scripts are for demonstration purposes only
3. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
4. The deployment scripts are designed for both on-premises and cloud environments
5. The repository is used for educational/demonstration purposes as indicated by the main README
6. The Chef InSpec tests are critical for compliance validation and must be maintained in some form
7. The existing Ansible playbooks follow older patterns and could benefit from modernization (using collections, more structured roles, etc.)