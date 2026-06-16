# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that will need to be converted to Ansible roles.

Estimated timeline: 1-2 weeks for a single developer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verify**:
    - Description: Chef InSpec test profile that validates the HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-security**:
    - Description: Chef InSpec profile that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use Ansible's `assert` module
  - For more complex compliance testing: Integrate with Ansible Lint or Molecule
  - Alternative: Convert InSpec tests to equivalent Ansible roles that perform the same validation checks

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles with various drivers including Vagrant

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are correctly maintained in the Ansible role
  - Consider expanding the security hardening to include modern best practices

- **SSH Security**: The SSH security profile tests need to be converted to equivalent Ansible checks
  - Create an Ansible role that implements the same security controls for SSH
  - Include validation tasks that verify the SSH configuration meets security requirements

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible validation tasks
  - Challenge: InSpec has specialized resources for testing SSL/TLS configurations
  - Mitigation: Use Ansible's uri module with appropriate SSL options, or integrate with external tools like OpenSSL

- **Chef Server Deployment**: Converting Chef Server deployment scripts to Ansible roles
  - Challenge: The deployment scripts contain Chef-specific commands and configurations
  - Mitigation: Research equivalent Ansible modules or create custom scripts that can be executed via Ansible

### Migration Order

1. **website-https** (low risk, already in Ansible)
   - Convert to a proper Ansible role structure
   - Add documentation and improve variable naming

2. **poodle-fix** (low risk, already in Ansible)
   - Convert to a proper Ansible role structure
   - Consider merging with the website-https role as an optional security enhancement

3. **website-https-verify** (moderate complexity)
   - Convert InSpec tests to Ansible assertion tasks
   - Integrate with Molecule for testing

4. **ssh-security** (moderate complexity)
   - Convert InSpec profile to Ansible role with validation tasks
   - Ensure compliance with security standards is maintained

5. **chef-automate-deployment** and **chef-server-deployment** (high complexity)
   - Convert bash scripts to Ansible roles
   - Replace hardcoded credentials with Ansible Vault
   - Add proper error handling and idempotence

### Assumptions

1. The existing Ansible playbooks are functional and follow best practices
2. The InSpec tests are comprehensive and accurately validate the desired state
3. The target environment will continue to be Ubuntu 20.04 or compatible
4. The deployment scripts are intended for demonstration purposes and may contain simplified security practices
5. No external dependencies or integrations beyond what's visible in the repository
6. The migration will maintain the same level of security validation as the original code
7. No specific performance requirements are needed for the Ansible roles
8. The Chef Automate and Chef Server deployment scripts are used for demonstration and not production environments