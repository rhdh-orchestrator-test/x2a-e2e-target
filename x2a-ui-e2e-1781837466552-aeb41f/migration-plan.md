# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for deploying and configuring Apache web servers with HTTPS
2. Chef InSpec tests for validating security compliance of the deployed configurations

The migration complexity is low to moderate, as most of the infrastructure code is already in Ansible format. The primary migration task will be converting the Chef InSpec tests to Ansible-native testing solutions. Estimated timeline: 1-2 weeks for a single developer.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **apache-https-deployment**:
    - Description: Apache web server deployment with HTTPS configuration, self-signed certificates, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **poodle-vulnerability-fix**:
    - Description: Security patch for POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enforces TLSv1.2 for Apache

- **https-compliance-tests**:
    - Description: InSpec tests to validate HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL/TLS protocol verification

- **ssh-security-compliance**:
    - Description: InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Deployment script for Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing web server deployment. Migration consideration: Can be used as-is or templated in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: The deployment scripts suggest this environment was used for compliance reporting. Consider:
  - Ansible AWX/Tower for orchestration and reporting
  - Compliance scanning tools that integrate with Ansible (OpenSCAP, Lynis)

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Preserve the same SSL/TLS hardening in Ansible tasks

- **SSH Hardening**: InSpec tests validate SSH root login is disabled.
  - Migration approach: Create equivalent Ansible tasks to enforce and validate SSH security settings

- **Vault/secrets management**:
  - No encrypted secrets were detected in the repository
  - Self-signed certificates are generated during deployment
  - Hardcoded credentials found in setup scripts (username, password) should be moved to Ansible Vault

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing requires careful mapping of test assertions.
  - Mitigation: Create a test mapping document to ensure all compliance checks are preserved

- **Testing Framework**: Replacing Test Kitchen with Molecule requires reconfiguration of test scenarios.
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen setup

- **Chef Automate Replacement**: If compliance reporting is needed, an alternative to Chef Automate must be identified.
  - Mitigation: Evaluate Ansible AWX/Tower with compliance scanning integrations

### Migration Order

1. **apache-https-deployment** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Add documentation and variable parameterization

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate into main Apache playbook as a role or included task

3. **https-compliance-tests** (moderate complexity)
   - Convert InSpec tests to Ansible assert tasks or Molecule tests

4. **ssh-security-compliance** (moderate complexity)
   - Convert InSpec profile to Ansible tasks for both enforcement and validation

5. **chef-automate-deployment** and **chef-server-deployment** (high complexity)
   - Determine if these components are still needed
   - If needed, replace with Ansible AWX/Tower deployment playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.

2. The Chef Automate and Chef Server deployment scripts are examples and may not be actively used in the current workflow.

3. Test Kitchen is used primarily for development and testing, not for production deployments.

4. The security compliance requirements (such as STIG references in the SSH profile) are still relevant and should be preserved in the migration.

5. The target environment will continue to be Ubuntu 20.04 or compatible systems.

6. Self-signed certificates are acceptable for the web server configuration (production environments might require proper CA-signed certificates).

7. The hardcoded credentials in the setup scripts are for demonstration purposes only and would be replaced with proper secret management in production.