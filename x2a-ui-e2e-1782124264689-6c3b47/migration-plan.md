# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring a secure HTTPS website
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol validation, SSH root login security check

- **chef-automate-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use ansible-test for more comprehensive testing
  - Option 4: Keep InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for integration testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced
  - Disable older protocols (SSLv3)
  - Maintain proper certificate generation and management

- **SSH Security**: Preserve the SSH root login restrictions verified by the InSpec tests
  - Ensure PermitRootLogin is not set to 'yes'

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Recommendation: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec tests with equivalent Ansible testing mechanisms
  - Solution: Use a combination of Ansible assert modules and custom modules to verify compliance requirements
  - Alternative: Keep InSpec as a standalone tool and invoke it from Ansible playbooks

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be replaced with equivalent Ansible functionality
  - Solution: Create Ansible roles for Chef server deployment if still needed, or replace with Ansible AWX/Tower

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role structure for better organization

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Integrate with the website-https role as a security hardening task
   - Add idempotency improvements

3. **InSpec compliance tests** (moderate complexity)
   - Convert to Ansible assert statements or custom modules
   - Integrate with Molecule for testing

4. **Chef Automate deployment scripts** (high complexity)
   - Determine if Chef Automate is still needed or if it can be replaced with Ansible AWX/Tower
   - Create Ansible playbooks for deployment if Chef components are still required

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. The deployment scripts for Chef Automate may be educational rather than required components
4. Test Kitchen is used primarily for development and testing, not for production deployments
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and not used in production
6. The self-signed certificates are for testing and would be replaced with proper certificates in production