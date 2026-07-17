# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that demonstrate how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring a secure web server with HTTPS
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on standardizing the existing Ansible playbooks and converting the Chef InSpec tests to Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **inspec-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS content verification, SSL protocol verification, SSH configuration verification

- **chef-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file for web server testing
- `chef-and-ansible/README.md`: Documentation files explaining the purpose of the examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role testing
  - Use existing Vagrant driver if needed for consistency

- **Chef Automate/Infra Server**: Consider:
  - Ansible Tower/AWX for centralized management
  - GitLab CI/CD or GitHub Actions for pipeline automation

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the POODLE fix playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Security**: The InSpec profile checks for SSH root login restrictions
  - Ensure this security check is maintained in the Ansible-native testing solution

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for each InSpec resource and its Ansible equivalent

- **Chef Server Deployment**: The Chef server deployment scripts need to be replaced with Ansible roles
  - Mitigation: Create Ansible roles for Ansible Tower/AWX deployment that provide similar functionality

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize according to Ansible best practices
   - Add documentation and variable descriptions

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Integrate with the website-https playbook for a more cohesive solution
   - Add conditional logic for different Apache versions

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible-native testing solutions
   - Ensure all compliance checks are maintained

4. **Chef deployment scripts** (high complexity)
   - Replace with Ansible roles for deploying Ansible Tower/AWX
   - Create migration path for existing Chef data

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies
2. The InSpec tests are valuable and need to be preserved in some form
3. The deployment scripts for Chef Automate/Infra Server will be replaced with equivalent Ansible Tower/AWX deployment
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The security requirements (TLS 1.2, SSH restrictions) must be maintained
6. No external data sources or integrations are present beyond what's visible in the repository
7. The migration will maintain the same level of automation and testing coverage