# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single developer, with minimal complexity due to the small codebase and clear separation of concerns.

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

- **website-https-verification**:
    - Description: Chef InSpec test that validates the HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-security-profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation with security tags (STIG/CCI compliance)

- **chef-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the website deployment example

### Target Details

Analyzing the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with ansible-lint for static analysis
  - Use Molecule for integration testing
  - Implement Ansible assert modules for runtime validation
  - Consider ansible-test for comprehensive testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that can:
  - Configure equivalent monitoring and compliance solutions
  - Set up alternative configuration management if needed

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Maintain TLSv1.2 requirement and disable insecure protocols
  - Ensure certificate generation remains secure

- **SSH Hardening**: The SSH security profile must be converted to equivalent Ansible checks
  - Preserve STIG compliance tags and documentation
  - Maintain the security validation for SSH root login

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible assert module with careful condition mapping
  - Consider implementing custom Ansible modules for complex validations

- **Compliance Metadata**: Preserving STIG/CCI compliance information from InSpec controls
  - Mitigation: Use Ansible tags and documentation to maintain compliance metadata
  - Consider implementing a custom reporting mechanism for compliance data

- **Test Kitchen to Molecule**: Ensuring test scenarios are properly migrated
  - Mitigation: Create equivalent Molecule scenarios that match the Test Kitchen configurations
  - Validate that test coverage remains the same after migration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they can remain largely unchanged
2. **Test Infrastructure** - Replace Test Kitchen with Molecule
3. **InSpec Tests** - Convert to Ansible-native testing
4. **Chef Deployment Scripts** - Replace with Ansible equivalents

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance validation
2. The existing Ansible playbooks can remain largely unchanged
3. The deployment scripts for Chef Automate/Server need to be replaced with equivalent functionality
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant
5. No external data sources or integrations exist beyond what's visible in the repository
6. The security compliance requirements (STIG/CCI) must be maintained in the new solution
7. No complex state management or orchestration is required beyond what's in the current implementation