# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible components (which are already in Ansible format) and moderate complexity for converting the InSpec tests to Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Can be directly used in Ansible without modification.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider maintaining InSpec as a separate testing tool if deeply integrated

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Security**: Preserve the SSH root login restrictions from the InSpec test
  - Implement equivalent checks in Ansible or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require careful mapping of test assertions
  - Challenge: InSpec has specific resource types (like ssl, port) that need equivalent Ansible testing mechanisms
  - Mitigation: Use Ansible's uri module, wait_for module, and assert module to recreate similar tests

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Challenge: The deployment scripts are specific to Chef infrastructure
  - Mitigation: If Chef infrastructure is still needed, keep these scripts as-is; otherwise, replace with equivalent infrastructure (e.g., AWX/Ansible Tower)

### Migration Order

1. **website_https.yml** (Priority 1, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role structure for better organization

2. **poodle_fix.yml** (Priority 1, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https role as a security task

3. **InSpec Tests** (Priority 2, moderate complexity)
   - Convert website_https_verify.rb to Ansible/Molecule tests
   - Convert ssh_profile.rb to Ansible/Molecule tests

4. **Chef Deployment Scripts** (Priority 3, high complexity)
   - Determine if Chef infrastructure is still needed
   - If not, replace with Ansible Tower/AWX deployment

### Assumptions

1. The primary goal is to migrate all components to pure Ansible without dependencies on Chef tools
2. The InSpec tests are used for validation and compliance, not for active system configuration
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. Vagrant will continue to be used for development/testing environments
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives
6. The self-signed certificates in the website_https.yml playbook are for testing only and would be replaced with proper certificates in production
7. The Chef Automate and Chef Server deployment scripts may not need migration if the infrastructure is being completely replaced by Ansible