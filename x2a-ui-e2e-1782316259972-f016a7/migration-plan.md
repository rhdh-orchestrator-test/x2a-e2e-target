# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation, as referenced in a Progress Chef white paper. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The InSpec tests are straightforward, but ensuring equivalent test coverage in Ansible will require careful implementation.

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
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-security-profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled according to security standards
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the setup scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with ansible-lint for static analysis
  - Use Molecule for integration testing with testinfra as the verifier
  - Consider ansible-test for additional validation

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality specifically designed for Ansible

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or alternative solutions:
  - Consider AWX (open-source version of Ansible Tower) for web UI and API
  - Use GitLab CI/CD or Jenkins for automation pipelines
  - Implement Ansible Collections for organizing and distributing content

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the same level of protocol restriction (TLSv1.2 only)
  - Maintain handler notifications for service restarts

- **SSH Security Controls**: The SSH security profile must be maintained
  - Convert the InSpec control to equivalent Ansible assertions
  - Preserve the security metadata (STIG IDs, CCI references, impact levels)

- **Certificate Management**: Self-signed certificate generation must be preserved
  - Maintain the same directory permissions (/etc/apache2/certs with mode 0640)
  - Ensure proper key management practices

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 sets of credentials in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Challenge: InSpec provides domain-specific language for compliance testing
  - Mitigation: Use testinfra with Molecule for similar functionality, or implement custom Ansible modules for specialized tests

- **Compliance Metadata**: Preserving compliance metadata from InSpec controls
  - Challenge: InSpec has built-in support for compliance frameworks (STIG, CIS)
  - Mitigation: Create structured YAML files to store compliance metadata alongside Ansible tests

- **Test Coverage**: Ensuring the same level of test coverage after migration
  - Challenge: InSpec tests may use Ruby-specific features not available in Ansible
  - Mitigation: Create comprehensive test matrices and validate all test cases are covered

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - Low risk as these can remain largely unchanged
   - Update to use more modern Ansible practices (collections, fully qualified module names)

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb)
   - Convert to Molecule/testinfra tests
   - Validate they provide equivalent coverage

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh)
   - Convert to Ansible roles for infrastructure deployment
   - Implement Ansible Vault for credential management

4. **Test Kitchen Configuration** (kitchen.yml)
   - Replace with Molecule configuration
   - Update to use the new testing framework

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the existing Ansible playbooks
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. Vagrant will continue to be used for development/testing environments
4. The security compliance requirements (STIG references) must be preserved in the new solution
5. The Chef Automate and Chef Infra Server deployment scripts are intended for development/testing environments due to the hardcoded credentials
6. The migration does not require changes to the actual Apache configuration or SSL settings
7. No external data sources or integrations are present beyond what's visible in the repository
8. The existing Ansible playbooks follow older syntax patterns and would benefit from updates to newer Ansible practices