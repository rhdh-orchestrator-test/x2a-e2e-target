# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, primarily involving:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with HTTPS/SSL setup and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-remediation**:
    - Description: Security fix for POODLE vulnerability in SSL configurations
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enforces TLSv1.2

- **compliance-testing**:
    - Description: InSpec tests for verifying HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol validation, SSH root login security check

- **chef-infrastructure-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts using Chef tooling
    - Key Features: Chef Automate deployment, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file for website testing
- `README.md`: Documentation files explaining the repository purpose

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Maintain InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise orchestration
  - AWX (open source upstream of Ansible Tower) for smaller deployments

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Ensure TLSv1.2 enforcement is maintained
  - Consider updating to include TLSv1.3 support

- **SSH Security**: Maintain the SSH root login restrictions verified by InSpec tests
  - Implement equivalent checks using Ansible's assert module or ansible-lint

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username: 'jtonello', password: 'password')
  - Replace with Ansible Vault for secure credential storage
  - Consider integration with external secret management systems

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use Ansible's assert module with appropriate modules (uri, stat, command) to verify the same conditions
  - Consider maintaining InSpec as a verification tool called from Ansible if tests are complex

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible management
  - Mitigation: Document manual steps for Ansible Automation Platform setup or create equivalent playbooks

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Add idempotency improvements
   - Convert to Ansible role structure

2. **ssl-poodle-remediation** (low risk, already in Ansible)
   - Integrate with website-https role
   - Update to include newer security best practices

3. **compliance-testing** (moderate complexity)
   - Convert InSpec tests to Ansible assertions
   - Create verification playbooks

4. **chef-infrastructure-deployment** (high complexity)
   - Create Ansible playbooks for Ansible Automation Platform deployment
   - Document migration path from Chef Automate to Ansible Automation Platform

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are critical to maintain for compliance verification
3. The deployment scripts are examples and not used in production environments
4. No external Chef cookbooks or complex Chef-specific features are in use
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. No complex state management or data bags are in use
7. The migration will standardize on Ansible completely rather than maintaining a hybrid approach