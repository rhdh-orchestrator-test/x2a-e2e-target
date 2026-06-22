# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that will need to be replaced with Ansible-based deployment solutions.

Estimated timeline: 1-2 weeks for a single engineer, given the limited scope and straightforward nature of the components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS server deployment and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, compliance metadata (STIG, CCI references)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Simple HTML file used as a template for website deployment

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for test-driven development
  - Option 2: Ansible Assert module for runtime validation
  - Option 3: Integration with other testing frameworks like Serverspec or Testinfra

- **Test Kitchen**: Replace with Ansible-native testing orchestration:
  - Option 1: Ansible Molecule for test orchestration
  - Option 2: Simple Vagrant or Docker-based test environments managed directly by Ansible

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks:
  - Create equivalent Ansible roles for configuration management platform deployment
  - Consider migrating to AWX/Ansible Tower as a replacement for Chef Automate

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Maintain TLSv1.2 requirement and SSLv3 disablement
  - Consider updating to include TLSv1.3 support

- **SSH Hardening**: The SSH security controls in ssh_profile.rb need to be preserved
  - Convert STIG compliance checks to Ansible assertions or Ansible security role
  - Maintain compliance metadata for audit purposes

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Compliance Testing**: Converting Chef InSpec tests to Ansible-native testing while preserving compliance metadata
  - Mitigation: Use Ansible assert module with detailed comments or custom modules that can store compliance metadata

- **Test Orchestration**: Replacing Test Kitchen with an Ansible-native solution
  - Mitigation: Adopt Ansible Molecule which provides similar functionality for testing Ansible roles

- **Deployment Scripts**: Converting Chef Automate/Server deployment to Ansible
  - Mitigation: Create Ansible roles that perform equivalent system configuration and package installation

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already Ansible)
   - Review and update to current Ansible best practices
   - No actual migration needed, just potential modernization

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible security role or assertions

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Consider if Chef Automate/Server is still needed or if AWX/Tower should be used instead

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't require functional changes
2. The Chef InSpec tests are used primarily for validation and not for ongoing compliance monitoring
3. The deployment scripts are used for setting up development/test environments and not production systems
4. No external Chef cookbooks or complex Chef-specific features are in use
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
6. The security requirements represented in the InSpec tests must be preserved in the Ansible solution
7. No CI/CD pipeline integration is present in the current solution that would need migration