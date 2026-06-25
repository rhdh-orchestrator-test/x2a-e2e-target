# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate a secure web server configuration. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains straightforward Ansible playbooks and InSpec tests with clear purposes.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS server configuration and content
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use Ansible's `assert` module and `command` module with `register`
  - For more complex compliance testing: Integrate with Ansible Lint or Molecule for testing
  - Alternative: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
  - Molecule can use Vagrant as a driver similar to Test Kitchen

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Ensure the same level of TLS protocol restrictions are maintained
  - Consider updating to include newer TLS versions (TLS 1.3) if appropriate

- **SSH Hardening**: The SSH security controls from the InSpec profile need to be implemented in Ansible
  - Convert the InSpec SSH profile to Ansible security role or include in existing playbooks
  - Preserve the STIG compliance metadata for audit purposes

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username: 'jtonello', password: 'password')
  - These should be moved to Ansible Vault or another secure secret management solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible's testing capabilities
  - Challenge: InSpec has specialized resources for testing SSL/TLS configurations
  - Mitigation: Use Ansible's `uri` module with appropriate SSL parameters or custom modules

- **Compliance Metadata**: Preserving STIG compliance information from InSpec tests
  - Challenge: Ansible doesn't have a native way to store compliance metadata like InSpec
  - Mitigation: Use Ansible tags and documentation to preserve compliance information

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - No migration needed, but review for best practices and potential improvements

2. **poodle_fix.yml** (low risk, already Ansible)
   - No migration needed, but review for best practices and potential improvements

3. **website_https_verify.rb** (medium complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests

4. **ssh_profile.rb** (medium complexity)
   - Convert InSpec controls to Ansible security role or assertions

5. **chef-automate-deployment and chef-server-deployment** (high complexity)
   - Convert bash scripts to Ansible roles for deploying monitoring/compliance solutions
   - Consider replacing with Ansible AWX/Tower deployment if appropriate

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks are working correctly and don't need functional changes
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent functionality using Ansible or another tool
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Test Kitchen will be replaced with Molecule or another Ansible-native testing framework
6. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with secure credential management
7. The self-signed certificates in the web server deployment are acceptable for the use case