# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and clear separation of concerns.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Main module containing Ansible playbooks and InSpec tests for configuring and validating a secure web server
    - Path: chef-and-ansible
    - Technology: Ansible and Chef InSpec
    - Key Features: Apache configuration, SSL/TLS security, compliance testing

- **setup-automate**:
    - Description: Module containing deployment scripts for Chef Server and Chef Automate
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef infrastructure deployment, user and organization management

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/index.html`: Simple HTML file used as a test page for the web server. No migration needed as it's a static content file.
- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies HTTPS functionality and security configuration.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec control that verifies SSH root login is disabled for security compliance.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on setup-automate scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace `website_https_verify.rb` with Ansible assertion tasks or Molecule with Testinfra
  - Replace `ssh_profile.rb` with Ansible security roles or OpenSCAP integration

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality specifically designed for Ansible

- **Chef Automate/Server deployment scripts**: Replace with Ansible roles for infrastructure deployment
  - Create Ansible roles to deploy monitoring and compliance solutions that replace Chef Automate functionality

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enforced and older protocols disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Security Controls**: Preserve the SSH hardening checks from ssh_profile.rb
  - Convert STIG compliance checks to Ansible security role or OpenSCAP

- **Credentials Management**: 
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using Ansible's crypto modules

### Technical Challenges

- **Compliance Testing Framework**: Chef InSpec provides a domain-specific language for compliance testing that needs to be replaced
  - Solution: Use a combination of Ansible assert modules, Testinfra, and/or OpenSCAP
  - Challenge: Maintaining the readability and expressiveness of InSpec tests in Ansible

- **Test Kitchen to Molecule Migration**: Converting the test workflow
  - Solution: Create equivalent Molecule scenarios that match the current Test Kitchen configuration
  - Challenge: Ensuring test coverage remains consistent during migration

- **Chef Server/Automate Functionality**: Replacing Chef infrastructure components
  - Solution: Evaluate Ansible AWX/Tower or other open-source alternatives for similar functionality
  - Challenge: Feature parity for compliance reporting and dashboard functionality

- **Handler Name Inconsistency**: In poodle_fix.yml, the handler is named "Restart apache2" in the notify section but defined as "Restart apache" in the handlers section
  - Solution: Standardize handler names across all playbooks during migration

### Migration Order

1. **InSpec Tests** (chef-and-ansible/tests)
   - Convert to Ansible-native testing solutions first to establish the compliance framework
   - Low risk as these are tests, not production configuration

2. **Test Kitchen Configuration** (chef-and-ansible/kitchen.yml)
   - Replace with Molecule configuration after tests are migrated
   - Moderate complexity due to test environment setup requirements

3. **Chef Server/Automate Deployment Scripts** (setup-automate)
   - Create Ansible playbooks to replace the deployment scripts
   - Higher complexity due to infrastructure component dependencies

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) will remain largely unchanged, as they are already in the target technology.

2. The primary focus of the migration is replacing Chef InSpec tests with Ansible-native testing solutions.

3. The repository appears to be a demonstration/example repository rather than a production codebase, based on the README content and simple examples.

4. The Chef Server and Automate deployment scripts are included for demonstration purposes and may not be actively used in production.

5. No complex Chef cookbooks or recipes are present in the repository, simplifying the migration effort.

6. The migration will maintain the same level of security compliance checking currently provided by InSpec.

7. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.

8. No external data sources or integrations are referenced that would require additional migration planning.