# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and server deployment. The migration scope is relatively small, consisting primarily of:

1. Chef InSpec test profiles that validate compliance
2. Ansible playbooks for web server configuration
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and updating the shell scripts to deploy equivalent Ansible infrastructure.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Directory containing Ansible playbooks and InSpec tests for web server configuration and compliance
    - Path: chef-and-ansible
    - Technology: Ansible/Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Directory containing shell scripts for Chef Automate and Chef Infra Server deployment
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/index.html`: Sample HTML file used for testing web server configuration. Can be directly used in Ansible playbooks.
- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache with HTTPS using self-signed certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test profile that validates HTTPS configuration and security.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test profile that validates SSH security configuration.
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server.
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server without Automate.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use ansible-test for basic validation
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Maintain InSpec as a standalone tool and integrate with Ansible workflows

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Ansible Automation Platform for enterprise features
  - Git repositories for playbook/role storage

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Approach: Convert to an Ansible role with the same security parameters

- **SSH Hardening**: The SSH compliance tests must be maintained
  - Approach: Convert InSpec tests to equivalent Ansible assert tasks or maintain as separate compliance checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible assert modules or consider maintaining InSpec as a compliance tool alongside Ansible

- **Infrastructure Deployment**: Replacing Chef Automate/Infra Server with Ansible infrastructure
  - Mitigation: Create equivalent Ansible playbooks for AWX/Tower deployment

### Migration Order

1. **chef-and-ansible/website_https.yml** (already in Ansible format, low risk)
2. **chef-and-ansible/poodle_fix.yml** (already in Ansible format, low risk)
3. **chef-and-ansible/tests/website_https_verify.rb** (convert InSpec tests to Ansible assertions, moderate complexity)
4. **chef-and-ansible/tests/ssh_profile.rb** (convert InSpec tests to Ansible assertions, moderate complexity)
5. **setup-automate** scripts (create new Ansible playbooks for AWX/Tower deployment, high complexity)

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. The migration will replace Chef InSpec with Ansible-native testing or maintain InSpec as a standalone tool
3. The current Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and can be incorporated into the new Ansible structure with minimal changes
4. The deployment scripts for Chef infrastructure will be completely replaced with equivalent Ansible infrastructure deployment
5. No external Chef cookbooks or dependencies are being used beyond what's visible in the repository
6. The security compliance requirements will remain the same after migration
7. Test Kitchen will be replaced with Molecule or another Ansible-native testing framework