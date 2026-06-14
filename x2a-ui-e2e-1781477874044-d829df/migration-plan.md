# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Can be preserved as-is or included as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but run it from Ansible using the `command` or `shell` module

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with appropriate Ansible alternatives:
  - AWX/Ansible Tower for web UI and job scheduling
  - Ansible Galaxy for role sharing
  - GitLab CI/GitHub Actions for CI/CD pipelines

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the migration preserves the security hardening that disables SSLv3 and only enables TLSv1.2.
- **Self-signed Certificates**: The current implementation generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **SSH Security**: The InSpec profile checks for SSH root login configuration. Ensure this security check is preserved in the Ansible-based testing.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The deploy-automate.sh and deploy-chef-server.sh scripts contain hardcoded passwords that should be moved to Ansible Vault.
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional scripting or integration with other testing frameworks.
  - Mitigation: Consider using Ansible's assert module combined with command/shell modules to run similar checks, or maintain InSpec as a separate tool called from Ansible.

- **Test Kitchen to Molecule**: Transitioning from Test Kitchen to Molecule will require learning a new testing workflow.
  - Mitigation: Molecule is designed specifically for Ansible and provides similar functionality to Test Kitchen, making the transition relatively straightforward.

- **Chef Automate/Server Replacement**: Finding equivalent functionality in the Ansible ecosystem for Chef Automate's compliance and reporting features.
  - Mitigation: Consider a combination of AWX/Tower with additional tools like Prometheus/Grafana for monitoring and compliance reporting.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to improve structure and follow best practices.
2. **Testing Framework**: Replace Test Kitchen with Molecule and set up the testing environment.
3. **InSpec Tests**: Convert InSpec tests to Ansible-compatible testing or integrate InSpec with Ansible.
4. **Deployment Scripts**: Convert the Chef Automate and Chef Server deployment scripts to Ansible playbooks.

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool, eliminating the dependency on Chef.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functional and follow best practices, requiring minimal changes.
3. The InSpec tests are valuable and their functionality should be preserved, either by converting to Ansible-native testing or by calling InSpec from Ansible.
4. The deployment scripts for Chef Automate and Chef Server need to be replaced with equivalent Ansible functionality or alternative tools.
5. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
6. No specific cloud provider is targeted, as the current configuration appears to be platform-agnostic.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with Ansible Vault in the production environment.
8. The self-signed certificates used in the website_https.yml playbook are acceptable for the use case, but might need to be replaced with proper certificates in production.