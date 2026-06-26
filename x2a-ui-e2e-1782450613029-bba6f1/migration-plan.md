# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains Chef Automate and Chef Infra Server deployment scripts.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests. The estimated timeline for migration would be 1-2 weeks, with low complexity for the Ansible components (which are already in Ansible format) and moderate complexity for converting the InSpec tests to Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the scripts mention they can be used on "on-prem or cloud VM"

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For basic tests: Use the Ansible `assert` module
  - For more complex compliance testing: Consider using ansible-lint, Molecule testing framework, or integrating with other compliance tools like OpenSCAP

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing
  - Molecule provides similar functionality for testing Ansible roles and playbooks
  - Can use the same Vagrant driver for local testing

- **Chef Automate/Infra Server**: Consider alternatives:
  - Ansible AWX/Tower for orchestration and management
  - Compliance scanning can be handled by OpenSCAP or similar tools integrated with Ansible

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security controls tested by the InSpec profile need to be implemented in Ansible
  - Ensure PermitRootLogin is properly configured
  - Maintain compliance with security standards referenced (SRG-OS-000112, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping
  - Challenge: InSpec has specific matchers and resources that may not have direct equivalents in Ansible
  - Mitigation: Use a combination of Ansible assert module, custom modules, and external testing tools

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting
  - Challenge: Chef Automate provides integrated compliance reporting that needs an equivalent in the Ansible ecosystem
  - Mitigation: Consider using Ansible AWX/Tower with compliance scanning plugins or integration with tools like OpenSCAP

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they are already in Ansible format
   - Review and optimize according to best practices
   - Update any deprecated syntax or modules

2. **Testing Framework** - Replace Test Kitchen with Molecule
   - Create equivalent Molecule configuration to replace kitchen.yml
   - Set up the same Ubuntu 20.04 Vagrant environment

3. **InSpec Tests** - Convert to Ansible testing
   - Convert website_https_verify.rb to Ansible assertions or Molecule verifiers
   - Convert ssh_profile.rb to Ansible security checks

4. **Chef Deployment Scripts** - Create Ansible playbooks for Chef infrastructure
   - Create playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to move all functionality to Ansible, eliminating the dependency on Chef InSpec
2. The target environment will continue to be Ubuntu 20.04 running on Vagrant for testing
3. The security requirements and compliance standards referenced in the InSpec tests must be maintained
4. The Chef Automate and Chef Infra Server deployment scripts are intended to be migrated to Ansible playbooks
5. No additional Chef cookbooks or resources are present beyond what's visible in the repository
6. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes