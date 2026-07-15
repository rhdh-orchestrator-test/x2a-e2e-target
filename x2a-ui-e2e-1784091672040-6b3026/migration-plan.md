# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used for compliance automation alongside Ansible deployments. The migration scope is relatively small, focusing on consolidating the existing Ansible playbooks and replacing Chef InSpec tests with Ansible-native testing solutions. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that part of the infrastructure is already using Ansible.

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
    - Description: Chef InSpec test that validates HTTPS website deployment and security configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH server security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for website deployment testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for testing
  - Convert InSpec controls to Ansible assertions or custom modules
  - Consider using ansible-lint for static code analysis

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
  - Molecule can handle the provisioning, converge, and verify phases

- **Chef Automate/Infra Server**: If compliance reporting is needed, consider:
  - Ansible AWX/Tower for orchestration and reporting
  - OpenSCAP integration with Ansible for compliance scanning
  - Prometheus and Grafana for monitoring and dashboards

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enforced and SSLv3 remains disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Hardening**: Maintain the SSH security controls from the InSpec profile
  - Convert the InSpec control to an Ansible role that both configures and validates SSH settings
  - Include STIG compliance metadata in Ansible roles

- **Certificate Management**: The self-signed certificate generation should be maintained
  - Consider enhancing with Let's Encrypt integration for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - No other credentials were detected in the repository

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible assert module for basic tests and custom modules for more complex validations
  - Consider ansible.builtin.uri module to replace HTTP/HTTPS validation tests

- **Compliance Reporting**: Loss of Chef InSpec's compliance reporting capabilities
  - Mitigation: Implement OpenSCAP with Ansible for compliance scanning and reporting
  - Consider AWX/Tower for centralized reporting and dashboards

- **Test Kitchen Replacement**: Ensuring Molecule provides equivalent testing capabilities
  - Mitigation: Create comprehensive Molecule scenarios that match current Test Kitchen functionality
  - Document the new testing workflow for team adoption

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle_fix.yml** (low risk, already Ansible): Review and potentially merge with the website_https playbook
3. **Chef InSpec Tests** (moderate complexity): Convert to Ansible Molecule tests
4. **Chef Automate Deployment** (high complexity): Replace with Ansible AWX/Tower deployment playbooks

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The target environment is Ubuntu 20.04 running on Vagrant VMs
3. There is no current integration with external systems beyond what's visible in the repository
4. The security controls implemented are for demonstration purposes and may need enhancement for production use
5. The Chef Automate and Chef Server deployment scripts are used for setting up test environments
6. No custom InSpec resources or complex dependencies exist beyond what's visible in the test files
7. The migration will consolidate all functionality into pure Ansible without maintaining Chef InSpec