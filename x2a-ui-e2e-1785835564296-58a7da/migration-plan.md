# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and demonstration purposes. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that part of the codebase is already using Ansible.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS response testing, SSL protocol verification

- **deploy-automate**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/README.md`: Documentation explaining the purpose of the Chef InSpec and Ansible integration examples.
- `README.md`: Main repository documentation explaining the purpose of the Chef examples.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks like:
  - Molecule for Ansible role testing
  - ansible-lint for static analysis
  - testinfra for infrastructure testing (Python-based alternative to InSpec)

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Configure system requirements
  - Install and configure equivalent functionality using:
    - AWX/Ansible Tower for web UI and job scheduling
    - GitLab CI or Jenkins for pipeline integration
    - Compliance scanning using OpenSCAP or similar tools

### Security Considerations

- **SSL Configuration**: The migration must maintain the same level of security in the SSL configuration:
  - Disable vulnerable protocols (SSL3, TLS 1.0, TLS 1.1)
  - Enable only TLS 1.2 or higher
  - Maintain proper certificate generation and management

- **SSH Hardening**: Ensure SSH security controls are maintained:
  - Disable root login
  - Implement proper authentication mechanisms
  - Maintain compliance with security requirements (SRG-OS-000112, V-38607)

- **Vault/secrets management**: 
  - Current implementation has hardcoded credentials in the deployment scripts
  - Migration should use Ansible Vault for securing:
    - User passwords in the Chef server deployment scripts
    - Any other sensitive information

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to equivalent Ansible testing tools:
  - Challenge: InSpec has specific resource types and matchers that may not have direct equivalents
  - Mitigation: Map InSpec resources to testinfra or other Python testing libraries, potentially write custom modules

- **Maintaining Compliance Validation**: Ensuring the same level of compliance checking:
  - Challenge: InSpec is specifically designed for compliance testing
  - Mitigation: Use OpenSCAP, testinfra, or other compliance tools integrated with Ansible

- **Chef Server Functionality**: Replacing Chef Server functionality:
  - Challenge: Chef Server provides specific features for node management and policy distribution
  - Mitigation: Implement equivalent functionality using AWX/Tower or other Ansible management tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Low risk as they're already in Ansible format
   - Only need review and potential refactoring to follow best practices

2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb):
   - Convert to testinfra or other Ansible-compatible testing framework
   - Update Kitchen configuration to use the new testing framework

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh):
   - Highest complexity due to the need to replace Chef-specific functionality
   - Create Ansible playbooks that provide equivalent infrastructure management capabilities

### Assumptions

1. The primary goal is to consolidate on Ansible as the single automation tool, eliminating Chef components.
2. The InSpec tests are used for compliance validation and their functionality needs to be preserved.
3. The deployment scripts are used for setting up Chef infrastructure which will be replaced with Ansible-managed infrastructure.
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions.
5. The security requirements specified in the InSpec tests must be maintained in the migrated solution.
6. The current implementation is used for demonstration or educational purposes rather than production, based on the repository description.
7. No external data sources or complex integrations are present beyond what's visible in the repository.