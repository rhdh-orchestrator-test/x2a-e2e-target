# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verification**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-security-profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation with security tags (STIG compliance)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework configuration
- `index.html`: Simple HTML file used as a template for website deployment - can be preserved as-is or incorporated into Ansible templates

### Target Details

Analyzing the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality for Ansible playbooks as Test Kitchen does for Chef

- **Chef Automate/Infra Server**: Replace with Ansible automation platform
  - Consider AWX/Tower for web UI and API
  - Use Ansible collections for configuration management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to include TLSv1.3 support

- **SSH Security**: Preserve the SSH hardening checks from the InSpec profile
  - Convert the STIG compliance checks to Ansible assertions or Molecule tests
  - Maintain compliance metadata (CCI numbers, STIG IDs)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username: jtonello, password: password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Challenge: InSpec's resource-based testing is more concise than Ansible's module-based approach
  - Mitigation: Use Molecule's verifier plugins or create custom Ansible modules for testing

- **Compliance Metadata**: Preserving compliance metadata from InSpec tests
  - Challenge: InSpec has built-in support for compliance metadata that Ansible lacks
  - Mitigation: Use YAML comments or custom variables to store compliance metadata in Ansible playbooks

- **Certificate Management**: Ensuring secure certificate handling
  - Challenge: The current implementation generates self-signed certificates inline
  - Mitigation: Use Ansible Vault to store certificates or implement a more robust certificate management solution

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible roles/playbooks
4. **Test Infrastructure** (kitchen.yml) - Replace with Molecule configuration

### Assumptions

1. The current Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require significant changes
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. The security requirements (TLS 1.2, SSH hardening) will remain the same
4. There is no integration with external systems beyond what's visible in the repository
5. The Chef Automate and Chef Infra Server deployment is for demonstration purposes and not production use (given the hardcoded credentials)
6. The migration is primarily focused on replacing Chef InSpec with Ansible-native testing while preserving the existing Ansible playbooks
7. No additional Chef cookbooks or resources are being used beyond what's visible in the repository