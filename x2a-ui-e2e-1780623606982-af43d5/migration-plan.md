# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that will need to be replaced with Ansible-based deployment solutions.

The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity. The primary challenge will be converting the InSpec compliance tests to equivalent Ansible testing mechanisms while maintaining the same level of security validation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test for validating HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response validation, SSL protocol security checks

- **ssh_profile**:
    - Description: Chef InSpec test for validating SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing web server deployment. Can be preserved as-is or integrated into Ansible content.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM targets

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use Ansible assert module
  - For more complex compliance testing: Integrate with Ansible Lint or Molecule
  - For comprehensive compliance: Consider integrating with OpenSCAP or using ansible-compliance collection

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles with various drivers and verifiers

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks
  - Consider using community-maintained Ansible roles for deploying alternative compliance platforms

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain the same level of security validation

- **SSH Security**: The SSH compliance checks must be preserved
  - Convert the InSpec SSH root login check to equivalent Ansible assertions
  - Preserve the STIG compliance metadata for audit purposes

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate generation should use Ansible's crypto modules with proper secret management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Solution: Use Ansible assert module for basic tests, consider ansible-test or Molecule for more complex validations

- **Compliance Metadata**: Preserving STIG and CCI compliance metadata from InSpec tests
  - Solution: Use Ansible tags and custom variables to maintain compliance metadata

- **Test Kitchen Integration**: Replacing the Test Kitchen workflow
  - Solution: Implement Molecule testing framework with similar driver (Vagrant) and create equivalent test scenarios

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format
   - Review and update as needed for best practices
   - Integrate with Ansible Vault for any sensitive data

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible assertions or Molecule tests
   - Ensure all security checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Create Ansible playbooks to replace Chef Automate/Server deployment
   - Consider alternative compliance platforms that integrate with Ansible

4. **Test Infrastructure** (kitchen.yml): Moderate complexity
   - Replace with Molecule configuration
   - Ensure test scenarios match original functionality

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.

2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and follow best practices.

3. The Chef InSpec tests are the main components that need migration to Ansible-native testing.

4. The deployment scripts for Chef Automate and Chef Server are used for setting up a test environment and will need replacement with equivalent Ansible functionality.

5. There is no complex data structure or state management that would require special handling during migration.

6. The security compliance requirements (STIG, CCI) need to be preserved in the migrated solution.

7. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.

8. No external integrations or APIs are being used that would require special handling.