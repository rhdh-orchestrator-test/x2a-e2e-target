# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing rather than being a pure Chef cookbook repository. The migration scope is relatively small, as most of the infrastructure code is already in Ansible format, with Chef components primarily being used for testing and compliance validation.

**Timeline Estimate**: 1-2 weeks for a complete migration, with minimal complexity due to the limited Chef components and the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 for security

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests together
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with testinfra for testing
  - Option 2: Keep InSpec but integrate with Ansible directly rather than through Test Kitchen

- **Test Kitchen**: Replace with Ansible-native testing frameworks:
  - Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Migrate Chef Automate functionality to Ansible Automation Platform
  - Replace Chef Server with Ansible Tower/AWX for centralized management

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enforced and SSLv3 remains disabled
  - Maintain the same level of Apache security configuration

- **SSH Security**: The SSH security controls tested by the InSpec profile must be implemented in Ansible
  - Ensure root login remains disabled
  - Maintain compliance with the security standards referenced (SRG-OS-000112, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Challenge: InSpec has specific syntax for compliance testing that may not directly map to other testing frameworks
  - Mitigation: Consider using Ansible Molecule with testinfra, which provides similar functionality, or maintain InSpec as a separate testing tool

- **Test Kitchen Integration**: Replacing Test Kitchen with Ansible-native testing tools
  - Challenge: Test Kitchen provides a specific workflow that integrates Ansible and InSpec
  - Mitigation: Ansible Molecule can provide similar functionality with proper configuration

- **Chef Automate Functionality**: Ensuring all Chef Automate functionality is covered
  - Challenge: Chef Automate provides specific compliance and reporting features
  - Mitigation: Map these features to Ansible Automation Platform capabilities or supplement with additional tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to improve structure and follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible Molecule tests or maintain as standalone InSpec tests with direct Ansible integration
3. **Chef Automate/Server Deployment Scripts**: Convert bash scripts to Ansible roles for deploying alternative infrastructure

### Assumptions

1. The primary goal is to move away from Chef components while maintaining the same functionality
2. The existing Ansible playbooks are working correctly and don't need significant rework
3. The security and compliance requirements represented in the InSpec tests must be maintained
4. Test Kitchen is being used primarily for development and testing, not for production deployments
5. The deployment scripts for Chef Automate/Server are used for setting up infrastructure and can be replaced with equivalent Ansible roles
6. The repository is primarily a demonstration of Chef InSpec with Ansible rather than a production infrastructure codebase
7. No external Chef cookbooks or dependencies are being used beyond what's visible in the repository
8. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in production