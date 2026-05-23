# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that demonstrate how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Ansible playbooks for web server configuration with HTTPS
2. Chef InSpec tests for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec-website-tests**:
    - Description: Chef InSpec tests that verify HTTPS functionality and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response validation, SSL protocol security checks

- **inspec-ssh-profile**:
    - Description: Chef InSpec profile that verifies SSH security compliance (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance checks

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks or adapting to use Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Can be directly incorporated into Ansible content.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or alternative compliance solutions:
  - Option 1: Migrate to Ansible Automation Platform for centralized management
  - Option 2: Use AWX (open-source Ansible Tower) for workflow management
  - Option 3: Implement GitLab CI/CD or Jenkins for automation pipelines

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols remain disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: Preserve the SSH security controls verified by the InSpec profile
  - Ensure root login remains disabled
  - Consider expanding SSH hardening based on the STIG requirements referenced in the InSpec profile

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Compliance Testing**: The primary challenge is maintaining the compliance testing functionality currently provided by InSpec
  - Solution: Either maintain InSpec as a separate tool or implement equivalent tests using Ansible's assert module and custom modules

- **Certificate Management**: The current solution generates self-signed certificates
  - Solution: Implement proper certificate management using Ansible's crypto modules or integrate with external certificate authorities

- **User Management**: The Chef server scripts create users and organizations
  - Solution: Implement equivalent user management in Ansible Automation Platform or alternative solution

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Add additional documentation and variable parameterization

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Consider merging with the website-https playbook for a consolidated approach
   - Enhance with additional security hardening measures

3. **InSpec tests** (moderate complexity)
   - Evaluate options for replacing or maintaining InSpec tests
   - Implement chosen testing strategy

4. **Chef Automate/Server deployment scripts** (high complexity)
   - Determine replacement strategy for Chef Automate/Server functionality
   - Implement Ansible playbooks for the chosen solution

### Assumptions

1. The primary goal is to consolidate on Ansible while maintaining the compliance testing capabilities
2. The current setup is used for demonstration/educational purposes rather than production
3. The hardcoded credentials in the deployment scripts are not used in production environments
4. The self-signed certificates are acceptable for the current use case
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The SSH compliance requirements are based on RHEL STIG standards but are being applied to Ubuntu systems
7. Test Kitchen is only used for development/testing and not for production deployments