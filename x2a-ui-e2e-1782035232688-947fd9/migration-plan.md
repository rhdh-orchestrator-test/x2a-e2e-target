# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-website-tests**:
    - Description: Chef InSpec tests that validate HTTPS functionality and security of the deployed web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS content validation, SSL protocol security checks

- **inspec-ssh-profile**:
    - Description: Chef InSpec profile that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
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
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use Ansible assert module and register variables
  - For more complex compliance testing: Integrate with Ansible Lint or Molecule for testing
  - Alternative: Convert InSpec tests to Python-based tests using pytest or similar frameworks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
  - Molecule provides similar functionality for testing Ansible roles and playbooks
  - Can use the same Vagrant driver for local testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform
  - Convert deployment scripts to Ansible playbooks for installing Ansible Automation Platform
  - Create roles for user management similar to the Chef user/org creation

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to include TLSv1.3 support for newer systems

- **SSH Hardening**: The SSH security profile must be maintained
  - Convert the InSpec SSH profile to Ansible security role or include in existing playbooks
  - Preserve STIG compliance metadata for reporting

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with carefully constructed tests that match InSpec's intent
  - Consider using community.general.assert module for more complex assertions

- **Compliance Metadata**: Preserving STIG and CCI compliance metadata from InSpec tests
  - Mitigation: Document compliance requirements separately or use Ansible tags and variables to store metadata

- **Test Kitchen to Molecule**: Adapting the testing workflow
  - Mitigation: Create equivalent Molecule scenarios that match the Test Kitchen configuration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-compatible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible playbooks for Ansible Automation Platform deployment
4. **Test Infrastructure** (kitchen.yml) - Replace with Molecule configuration

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment
2. The existing Ansible playbooks are functioning correctly and don't require significant changes
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The deployment scripts for Chef Automate and Chef Infra Server are intended to be replaced with equivalent Ansible Automation Platform deployment
5. No external dependencies or integrations beyond what's visible in the repository
6. The security requirements (TLS configuration, SSH hardening) must be maintained in the migrated solution
7. Test Kitchen is only used for development/testing and not for production deployments