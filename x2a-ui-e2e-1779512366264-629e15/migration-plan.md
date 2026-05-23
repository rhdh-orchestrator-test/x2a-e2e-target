# MIGRATION FROM CHEF INSPEC TO ANSIBLE

## Executive Summary

This repository contains a demonstration of using Chef InSpec alongside Ansible for compliance automation. The migration scope is relatively small, focusing on converting InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server setup scripts that need to be migrated to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope of the repository.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-inspec-tests**:
    - Description: Chef InSpec tests for validating HTTPS website configuration and SSH security settings
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL/TLS protocol verification, SSH configuration compliance checks

- **ansible-https-website**:
    - Description: Ansible playbook for deploying a secure HTTPS website with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ansible-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL configuration hardening, service restart handlers

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML content for the website deployment. Can be reused as-is in the Ansible migration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider Ansible's integration with OpenSCAP for compliance scanning

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality to Test Kitchen but is designed specifically for Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and configuration

- **SSH Hardening**: The SSH security profile tests must be converted to equivalent Ansible checks
  - Focus on maintaining the PermitRootLogin restriction
  - Preserve compliance with security standards referenced in the InSpec profile (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - The deploy scripts contain hardcoded credentials (username, password) that should be moved to Ansible Vault
  - No encrypted data bags or Chef Vault usage detected
  - 2 credential sets identified in the deployment scripts (user credentials)

### Technical Challenges

- **Test Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Challenge: InSpec has a domain-specific language for compliance testing that doesn't directly map to Ansible
  - Mitigation: Use a combination of Ansible assert modules and custom scripts to achieve similar functionality

- **Chef Automate/Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Challenge: The scripts perform Chef-specific operations that need Ansible equivalents
  - Mitigation: Research Ansible roles for deploying Chef components or consider replacing with pure Ansible infrastructure

### Migration Order

1. **ansible-https-website** and **ansible-poodle-fix** (low risk, already in Ansible)
   - These are already Ansible playbooks and only need minor adjustments for best practices
   - Consolidate into a single playbook with roles for better organization

2. **chef-inspec-tests** (moderate complexity)
   - Convert InSpec tests to Ansible-compatible testing framework
   - Ensure all compliance checks are maintained

3. **chef-automate-setup** and **chef-server-setup** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement Ansible Vault for credential management
   - Consider whether Chef components are still needed or can be replaced with Ansible equivalents

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are intended to be kept and enhanced rather than replaced
3. The Chef Automate and Chef Infra Server deployment scripts are still relevant and needed in the migrated solution
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The security compliance requirements (SSH hardening, SSL/TLS configuration) must be maintained in the migrated solution
6. No external data sources or integrations beyond what's visible in the repository are required
7. The migration will not introduce new features but focus on maintaining existing functionality
8. Test Kitchen is used primarily for development/testing and not for production deployments