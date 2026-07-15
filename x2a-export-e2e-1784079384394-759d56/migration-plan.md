# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also includes Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

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
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Sample HTML file used in the website deployment. Can be preserved as-is or converted to a template.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For website_https_verify.rb: Use Ansible's uri module and assert module for HTTP checks
  - For SSL protocol verification: Use Ansible's community.crypto.openssl_info module
  - For ssh_profile.rb: Use Ansible's lineinfile or template module with assert for validation

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule supports Vagrant driver similar to Test Kitchen
  - Provides similar functionality for testing Ansible roles

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in poodle_fix.yml
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: Maintain the SSH root login restrictions from ssh_profile.rb
  - Convert the InSpec control to an Ansible task that ensures PermitRootLogin is not set to 'yes'

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deployment scripts

- **Certificate Management**: Self-signed certificates are generated in website_https.yml
  - Preserve the certificate generation logic using Ansible's crypto modules
  - Consider adding option for using Let's Encrypt for production environments

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions
  - Challenge: InSpec provides a domain-specific language for compliance testing
  - Mitigation: Use combination of Ansible modules (uri, stat, command) with assert module to replicate tests
  - Consider using ansible-lint for static analysis

- **Chef Automate Deployment**: Converting Chef Automate deployment scripts to Ansible
  - Challenge: Chef Automate has specific system requirements and configuration
  - Mitigation: Create Ansible roles that handle system preparation, download and installation of Chef Automate

- **Test Framework Migration**: Moving from Test Kitchen to Molecule
  - Challenge: Different syntax and workflow between Test Kitchen and Molecule
  - Mitigation: Create equivalent Molecule scenarios for each Test Kitchen suite

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format
   - Review and update to current Ansible best practices
   - Add documentation and improve variable naming

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible assertions or custom modules
   - Ensure they provide equivalent validation

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement Ansible Vault for credential management

4. **Testing Framework** (kitchen.yml): Final step
   - Replace with Molecule configuration
   - Create equivalent test scenarios

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't require functional changes
3. The deployment scripts are used for setting up test environments and not production systems
4. The hardcoded credentials in deployment scripts are for demonstration purposes only
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The migration doesn't require changes to the actual web application functionality
7. There are no external dependencies or integrations not visible in the provided files
8. The SSH compliance check is a standalone test and not part of a larger compliance framework