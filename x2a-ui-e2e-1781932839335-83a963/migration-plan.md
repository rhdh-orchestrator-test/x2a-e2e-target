# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation, as referenced in the README. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for deploying and securing Apache web servers
2. Chef InSpec tests for validating security compliance

Additionally, there are Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and clear separation of concerns.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server deployment with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Security patch for Apache SSL configuration to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 protocol

- **compliance-tests**:
    - Description: InSpec tests for validating HTTPS configuration and SSH security settings
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS content verification, SSL protocol validation, SSH root login security check

- **chef-server-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts using Chef CLI tools
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML content for the web server

### Target Details

Analyzing the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (based on comments in deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Replace InSpec tests with equivalent Ansible assert modules or molecule tests
  - Consider ansible-lint for static code analysis
  - For compliance testing, evaluate OpenSCAP integration with Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipelines (GitHub Actions, GitLab CI, etc.)

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab/GitHub for code repository management
  - Consider Red Hat Satellite if RHEL systems are in use

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to include TLSv1.3 support

- **SSH Hardening**: The SSH security profile must be maintained
  - Ensure root login remains disabled
  - Maintain compliance with security benchmarks referenced in the InSpec tests (SRG-OS-000112, RHEL-08-000227)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods
  - Challenge: InSpec provides a domain-specific language for compliance testing that doesn't directly map to Ansible
  - Mitigation: Use a combination of Ansible assert modules, custom modules, and potentially integrate with other testing frameworks like Molecule

- **Chef Server Replacement**: Replacing Chef Server functionality with Ansible equivalents
  - Challenge: Chef Server provides organization management and policy-based configuration that Ansible handles differently
  - Mitigation: Implement Ansible AWX/Tower with appropriate inventory organization and RBAC to replace Chef Server functionality

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role structure for better reusability

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Integrate with the website-https role as a security enhancement
   - Update to include modern TLS best practices

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all security checks are maintained

4. **Chef Server deployment scripts** (high complexity)
   - Replace with Ansible playbooks for AWX/Tower deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
3. The security requirements specified in the InSpec tests must be maintained in the migrated solution
4. The Chef Automate and Chef Server deployment is for demonstration purposes and can be replaced with equivalent Ansible management tools
5. No external data sources or integrations beyond what's visible in the code are required
6. The migration will be to pure Ansible without maintaining any Chef components
7. Test Kitchen can be fully replaced by Molecule or similar Ansible-native testing frameworks
8. The hardcoded credentials in the deployment scripts are for demonstration only and will be properly secured in the migrated solution