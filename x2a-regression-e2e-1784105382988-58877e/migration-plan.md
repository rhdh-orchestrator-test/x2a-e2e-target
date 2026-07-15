# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that will need to be replaced with Ansible automation.

Estimated timeline: 1-2 weeks for a single developer, with the majority of time spent on converting InSpec tests to equivalent Ansible testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website-https-verification**:
    - Description: Chef InSpec test that validates HTTPS website deployment and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh-security-profile**:
    - Description: Chef InSpec control that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for the web server deployment

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM usage

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks
  - Create equivalent Ansible roles for configuration management platform deployment

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain compliance with security standards

- **SSH Security Controls**: Preserve the SSH security controls from the InSpec profile
  - Convert STIG compliance metadata to Ansible security role
  - Implement equivalent checks for SSH root login restrictions

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed SSL certificates generated in the website_https.yml playbook
  - Consider using Ansible Vault to secure credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Challenge: InSpec's resource-based testing model doesn't directly map to Ansible
  - Mitigation: Use Ansible assert module with appropriate shell commands to validate the same conditions

- **Compliance Metadata**: Preserving STIG and CCI compliance metadata from InSpec tests
  - Challenge: Ansible doesn't have a native way to store compliance metadata
  - Mitigation: Use YAML comments or variables to store compliance data, or integrate with OpenSCAP

- **Test Kitchen to Molecule**: Converting Test Kitchen workflow to Molecule
  - Challenge: Different configuration formats and testing approaches
  - Mitigation: Create equivalent Molecule scenarios that match the Test Kitchen configuration

### Migration Order

1. **website-https and poodle-fix playbooks** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbooks
   - No conversion needed, just validation and potential refactoring

2. **InSpec tests to Ansible tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible security role with appropriate checks

3. **Chef deployment scripts to Ansible playbooks** (high complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Server deployment scripts
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than for production use
2. The hardcoded credentials in the deployment scripts are examples and not used in production
3. The self-signed certificates are for testing purposes only
4. The target environment is Ubuntu 20.04 as specified in kitchen.yml
5. The SSH security profile is intended to be used with the Ansible playbooks, though there's no explicit connection in the code
6. The repository is meant for educational/demonstration purposes based on the README content
7. No complex Chef cookbooks or recipes are present that would require significant conversion effort
8. The migration will maintain the same functionality but using Ansible-native approaches