# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verification**:
    - Description: Chef InSpec test that validates the HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-security-profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation with security tagging (STIG/CCI compliance)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for basic validation
  - Option 2: Implement Molecule for Ansible role testing
  - Option 3: Use pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Molecule for Ansible role testing and validation

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are maintained in the Ansible tasks
  - Consider updating to include more recent TLS versions (TLSv1.3) if supported

- **SSH Security**: The SSH root login check must be preserved in the Ansible testing framework
  - The STIG compliance tags should be maintained for audit purposes

- **Self-signed Certificates**: The certificate generation process should be preserved or enhanced
  - Consider adding certificate rotation or more secure key parameters

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 sets of credentials in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting the InSpec tests to Ansible assertions or Molecule tests
  - Challenge: Maintaining the same level of expressiveness and readability
  - Mitigation: Use Ansible's assert module with well-documented conditions or implement custom Molecule verifiers

- **Compliance Tagging**: Preserving the compliance metadata (STIG IDs, CCI numbers)
  - Challenge: Ansible doesn't have a native way to store compliance metadata like InSpec
  - Mitigation: Use YAML comments or custom variables to maintain the compliance mapping

- **Chef Automate Replacement**: Determining the appropriate Ansible-based alternative
  - Challenge: Chef Automate provides compliance scanning and reporting
  - Mitigation: Consider AWX/Ansible Tower with compliance scanning plugins or integrate with OpenSCAP

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible roles/playbooks
4. **Test Kitchen Configuration** (kitchen.yml) - Replace with Molecule configuration

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks are working correctly and don't require significant modifications
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent functionality using Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The security requirements (STIG/CCI compliance) must be maintained in the new implementation
6. No external integrations or APIs are being used that would require special handling
7. The self-signed certificates are acceptable for the environment (not production)