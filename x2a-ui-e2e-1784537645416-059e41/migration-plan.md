# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec testing that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks for a single engineer, as the codebase is relatively small and well-structured. The main challenge will be replacing Chef InSpec testing with equivalent Ansible testing solutions.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with Chef InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL certificate generation, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS website. Can be kept with minor modifications.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be kept with minor modifications.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website. Needs conversion to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs conversion to Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate deployment. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for Chef Infra Server deployment. Needs conversion to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule for testing infrastructure
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/Jenkins for CI/CD pipelines
  - Ansible collections for configuration management

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security practice should be maintained in the migrated solution.
  
- **SSH Hardening**: The InSpec profile checks for SSH root login disablement. This security check should be implemented in the Ansible solution.

- **Self-signed Certificates**: The current solution generates self-signed certificates. Consider integrating with Let's Encrypt for production environments.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate handling should use Ansible Vault for private keys

### Technical Challenges

- **InSpec Testing Replacement**: Finding equivalent testing capabilities in the Ansible ecosystem for compliance testing. Mitigation: Evaluate ansible-test, Molecule, and other testing frameworks to replace InSpec functionality.

- **Chef-specific Functionality**: Some Chef-specific features might not have direct equivalents in Ansible. Mitigation: Map Chef resources to Ansible modules and identify gaps early.

- **Maintaining Compliance Testing**: Ensuring the same level of compliance testing is maintained when migrating from InSpec. Mitigation: Create comprehensive test coverage with Ansible's testing tools.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml)
   - Low risk as they're already Ansible, just need testing framework changes
   - Update to use Ansible best practices and remove Chef InSpec dependencies

2. **Testing Framework** (chef-and-ansible/tests/*)
   - Convert InSpec tests to Ansible Molecule or equivalent testing framework
   - Ensure all compliance checks are maintained

3. **Chef Deployment Scripts** (setup-automate/*)
   - Convert bash scripts to Ansible playbooks
   - Implement Ansible Vault for credential management

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
2. Vagrant will continue to be used for development/testing environments.
3. The security compliance requirements will remain the same after migration.
4. There is no requirement to maintain backward compatibility with Chef InSpec.
5. The Chef Automate and Chef Infra Server functionality will be replaced by Ansible AWX/Tower or similar orchestration tools.
6. The current hardcoded credentials in scripts are for demonstration purposes only and will be properly secured in the migrated solution.
7. The Apache configuration and SSL settings are representative of production requirements.