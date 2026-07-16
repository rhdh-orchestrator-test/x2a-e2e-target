# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a template for the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with Testinfra for testing
  - Option 2: Use the ansible-test framework
  - Option 3: Implement equivalent tests using the Ansible assert module

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration
  - Molecule can manage the test instances and run the verification tests

- **Chef Automate/Infra Server**: Replace with Ansible Tower/AWX
  - Implement equivalent user management and organization structure in Ansible Tower/AWX
  - Consider migrating compliance data to Ansible Tower/AWX compliance features

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols disabled
  - Maintain the same level of security in the Apache configuration

- **SSH Security**: Preserve the SSH root login restrictions verified by the InSpec test
  - Implement equivalent Ansible tasks to enforce this security control
  - Consider using Ansible security roles from Ansible Galaxy

- **Credentials Management**: 
  - The deploy scripts contain hardcoded credentials (username, password) that should be moved to Ansible Vault
  - Count: 2 credential sets in deploy scripts (username/password combinations)

- **Certificate Management**:
  - Self-signed certificates are generated in the website_https.yml playbook
  - Consider implementing a more robust certificate management solution using Ansible Vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Challenge: InSpec has specific matchers and resources that may not have direct equivalents
  - Mitigation: Map InSpec resources to Ansible modules or Testinfra methods, preserving test intent

- **Compliance Reporting**: InSpec provides rich compliance reporting capabilities
  - Challenge: Maintaining the same level of compliance reporting in Ansible
  - Mitigation: Implement custom reporting using Ansible callbacks or integrate with compliance tools like OpenSCAP

- **Chef Server Functionality**: Replacing Chef Server organization and user management
  - Challenge: Chef Server has specific user/org concepts that don't directly map to Ansible
  - Mitigation: Use Ansible Tower/AWX teams and organizations, with custom inventory scripts if needed

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format
   - Only need to be reviewed and potentially optimized for current Ansible best practices

2. **Test Framework** (kitchen.yml): Moderate complexity
   - Replace with Molecule configuration for testing Ansible playbooks

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible-native testing solutions

4. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible playbooks for deploying alternative solutions (Ansible Tower/AWX)

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. Vagrant will continue to be used for development/testing environments
3. The security requirements (SSL protocols, SSH configuration) will remain the same
4. The organization is moving from Chef to Ansible completely, not maintaining a hybrid approach
5. Chef InSpec tests are being used for compliance validation only, not for broader infrastructure testing
6. The simple website deployment is representative of the complexity of the actual production workloads
7. No external data sources or integrations are present beyond what's visible in the repository
8. The hardcoded credentials in the deployment scripts are for demonstration purposes only
9. The Chef Automate and Chef Infra Server deployment is a standalone environment not integrated with other systems