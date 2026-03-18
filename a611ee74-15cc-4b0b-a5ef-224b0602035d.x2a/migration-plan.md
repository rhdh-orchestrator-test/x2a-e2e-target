# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, with the following breakdown:
- 2-3 days for converting InSpec tests to Ansible testing frameworks
- 2-3 days for converting Chef server deployment scripts to Ansible
- 2-3 days for testing and validation
- 1-2 days for documentation and knowledge transfer

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for the web server deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM targets

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that can:
  - Configure system settings (hostname, sysctl parameters)
  - Deploy alternative infrastructure management tools (AWX/Tower)

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain handler notifications for service restarts

- **SSH Hardening**: Convert the SSH InSpec profile to Ansible security checks
  - Preserve STIG compliance metadata in documentation or tags
  - Implement equivalent checks using Ansible's assert module

- **Self-signed Certificates**: Maintain the same level of certificate security
  - Use Ansible's openssl_* modules as already implemented

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's domain-specific language to Ansible assertions
  - Mitigation: Create custom Ansible modules or use community.general collection modules for specialized tests

- **Compliance Metadata**: Preserving STIG and CCI identifiers from InSpec tests
  - Mitigation: Use Ansible tags and documentation to maintain compliance metadata

- **Test Kitchen to Molecule**: Adapting the testing workflow
  - Mitigation: Create equivalent Molecule scenarios that match the Test Kitchen configuration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks are working correctly and don't require significant changes
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The deployment scripts for Chef Automate/Server need to be replaced with equivalent infrastructure management tools
5. No additional Chef cookbooks or resources are present beyond what's visible in the repository
6. The migration doesn't need to preserve Test Kitchen as the testing framework
7. The security and compliance requirements (STIG, CCI) need to be maintained in the migrated solution