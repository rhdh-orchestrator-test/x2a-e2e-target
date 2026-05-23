# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing rather than being a pure Chef cookbook repository. The migration scope is relatively small, as most of the infrastructure code is already in Ansible format, with Chef components primarily focused on testing and compliance validation.

**Estimated Timeline**: 1-2 weeks
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-native testing solutions

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
    - Key Features: SSL protocol configuration, service restart handlers

- **inspec_website_tests**:
    - Description: Chef InSpec tests that verify HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port testing, HTTP response validation, SSL protocol verification

- **inspec_ssh_profile**:
    - Description: Chef InSpec compliance profile for SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance tagging with STIG references

- **chef_automate_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef server commands
    - Key Features: Chef server setup, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on comments in setup scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Convert InSpec tests to Ansible assert tasks
  - Option 3: Use ansible-lint for static analysis and compliance checks

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure deployment
  - Consider migrating to Ansible Tower/AWX for web UI and control features

### Security Considerations

- **SSL Configuration**: The repository includes SSL hardening (POODLE mitigation)
  - Migration approach: Maintain the same SSL configuration parameters in Ansible tasks
  - Consider using Ansible's crypto modules instead of direct file editing

- **SSH Security**: InSpec tests for SSH root login restrictions
  - Migration approach: Convert to Ansible assert tasks or Molecule tests
  - Maintain compliance with security standards (STIG references)

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec's DSL to Ansible-native testing
  - Mitigation: Use Ansible's assert module or Molecule with testinfra for similar functionality
  - Example: Port checks can be done with Ansible's wait_for module

- **Compliance Reporting**: InSpec provides rich compliance reporting
  - Mitigation: Consider implementing custom reporting with Ansible callback plugins
  - Alternative: Use OpenSCAP with Ansible for compliance reporting

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - Low risk as they're already in Ansible format
   - May need refactoring to follow best practices (roles, variables)

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb)
   - Convert to Ansible-native testing solutions
   - Maintain compliance metadata and checks

3. **Chef Server Deployment Scripts**
   - Convert bash scripts to Ansible playbooks
   - Implement secure credential management

### Assumptions

1. The primary goal is to move away from Chef components while maintaining the same functionality
2. Compliance testing and reporting are critical requirements
3. The existing Ansible playbooks are functional and follow best practices
4. No external Chef cookbooks or dependencies are being used
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The deployment scripts are used for setting up test environments rather than production systems
7. The hardcoded credentials in deployment scripts are for demonstration purposes only