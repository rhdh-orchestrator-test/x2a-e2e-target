# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also includes Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Sample HTML file used in the website deployment. Can be preserved as-is or included as a template in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime verification: Convert InSpec tests to Ansible assert modules or use the community.general.assert_cmd module
  - For comprehensive compliance: Consider integrating with OpenSCAP or using the ansible-lockdown project

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles with various drivers including Vagrant

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Consider updating to include TLSv1.3 support

- **SSH Hardening**: The SSH root login check must be preserved
  - Convert the InSpec control to an Ansible task that checks and enforces the same policy
  - Maintain the STIG compliance references for documentation

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **InSpec to Ansible Conversion**: Converting InSpec tests to Ansible assertions requires careful mapping
  - Challenge: InSpec has rich matchers that may not have direct equivalents in Ansible
  - Mitigation: Use assert module with custom conditions or develop custom Ansible modules if needed

- **Compliance Reporting**: InSpec provides structured compliance reporting
  - Challenge: Replicating the compliance reporting capabilities in Ansible
  - Mitigation: Consider using ansible-lint with custom rules and generating reports with custom callback plugins

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity, convert to Ansible roles with proper variable management
3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Highest complexity, requires conversion to Ansible testing framework

### Assumptions

1. The existing Ansible playbooks are compatible with current Ansible versions and don't require significant updates
2. The Chef InSpec tests are used primarily for validation and not as part of a larger compliance framework
3. There is no integration with external Chef Automate instances for compliance reporting
4. The deployment scripts are used for standalone installations and not part of a larger infrastructure deployment
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and not used in production
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
7. The migration does not need to preserve Test Kitchen functionality if replaced with equivalent Ansible testing tools