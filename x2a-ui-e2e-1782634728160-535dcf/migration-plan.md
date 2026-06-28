# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec test profiles for compliance validation
2. Chef Automate/Chef Server deployment scripts

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, as the repository already contains Ansible playbooks that can be reused. The primary focus will be on replacing Chef InSpec tests with Ansible-compatible testing frameworks and converting Chef server deployment scripts to Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and shell scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https_verify**:
    - Description: InSpec tests for validating HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: InSpec compliance profile for SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, STIG compliance checks, CCI controls

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef CLI
    - Key Features: User creation, organization setup, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `website_https.yml`: Ansible playbook for configuring HTTPS on Apache web server
- `poodle_fix.yml`: Ansible playbook for remediating SSL POODLE vulnerability
- `index.html`: Sample HTML file used in web server configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for integration testing
  - Option 2: ansible-test for unit testing
  - Option 3: Maintain InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - Molecule already supports multiple drivers including Vagrant

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure setup
  - AWX/Ansible Tower for web UI and control plane

### Security Considerations

- **SSH Security Controls**: The SSH compliance profile needs to be converted to:
  - Ansible security roles from ansible-lockdown
  - DISA STIG roles for RHEL 8 compliance
  - CIS benchmark roles

- **SSL/TLS Configuration**: The HTTPS and POODLE fix configurations need to be:
  - Maintained in Ansible with proper variable management
  - Updated to include modern TLS best practices

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, possibly with ansible-vault or external secret management
  - Count of credentials detected: 3 (username, password, SSL keys)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing frameworks may require:
  - Learning curve for Molecule or other testing tools
  - Ensuring equivalent coverage of compliance checks
  - Mitigation: Start with simple tests and gradually convert complex ones

- **Compliance Reporting**: Chef InSpec provides rich compliance reporting that needs equivalent in Ansible:
  - Consider integration with tools like Compliance as Code
  - Evaluate AWX/Tower for compliance reporting capabilities
  - Mitigation: Implement custom reporting using Ansible callback plugins

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Already in Ansible format, just need review and optimization
2. **Chef Automate Deployment Scripts**: Convert bash scripts to Ansible playbooks
3. **InSpec Tests**: Convert to Ansible-compatible testing framework

### Assumptions

1. The repository is primarily a demonstration of Chef InSpec with Ansible rather than a production environment
2. No external Chef cookbooks or complex Chef-specific features are in use
3. The primary goal is to move all functionality to Ansible, including testing
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No complex data bags or Chef-specific secret management is in use
6. The deployment scripts are for demonstration purposes and may need enhancement for production use