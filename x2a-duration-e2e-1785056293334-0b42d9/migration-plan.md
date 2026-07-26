# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository is relatively small and appears to be primarily for demonstration purposes rather than a full production infrastructure. The migration scope is limited, with the main focus being on standardizing the existing Ansible playbooks and converting the Chef Automate and Chef Server deployment scripts to Ansible.

Estimated timeline: 1-2 weeks for a single engineer, given the limited scope and complexity.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

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

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality. Will need to be converted to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance profile for SSH security. Will need to be converted to Ansible-compatible testing framework.
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (based on comments in setup scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like:
  - Molecule for infrastructure testing
  - ansible-lint for static code analysis
  - Consider OpenSCAP or DISA STIG Ansible roles for compliance testing

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Ansible-compatible CI/CD pipelines

- **Chef Automate/Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - GitLab/GitHub for version control and CI/CD
  - Ansible Collections for role management

### Security Considerations

- **SSL Configuration**: The existing playbooks configure Apache with SSL. Ensure the migration maintains or improves the security posture:
  - Update the SSL configuration to use modern protocols (TLSv1.2 and TLSv1.3)
  - Use stronger cipher suites
  - Consider integrating with Let's Encrypt for certificate management

- **SSH Hardening**: The SSH compliance profile checks for root login restrictions. Ensure this security check is maintained in the Ansible implementation:
  - Create an Ansible role for SSH hardening
  - Implement idempotent checks for SSH configuration

- **Credentials Management**: The Chef deployment scripts contain hardcoded credentials:
  - Replace with Ansible Vault for secure credential storage
  - Consider integration with external secret management systems (HashiCorp Vault, AWS Secrets Manager, etc.)

- **Vault/secrets management**:
  - 1 hardcoded password in setup-automate scripts (userpassword variable)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - InSpec provides declarative testing that may require more procedural approaches in Ansible
  - Solution: Use Molecule with testinfra or serverspec plugins, or maintain InSpec as a separate testing tool

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents:
  - Chef Server provides a centralized configuration database
  - Solution: Use AWX/Tower for inventory management and job scheduling

- **Compliance Automation**: Maintaining compliance automation capabilities:
  - InSpec provides rich compliance testing capabilities
  - Solution: Integrate with OpenSCAP, DISA STIG Ansible roles, or maintain InSpec as a separate tool

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need standardization and best practices applied
2. **Testing Framework**: Convert InSpec tests to Ansible-compatible testing framework
3. **Chef Deployment Scripts**: Convert bash scripts to Ansible roles for deploying AWX/Tower

### Assumptions

1. The repository is primarily for demonstration purposes and not a production infrastructure
2. The InSpec tests are used for compliance verification of infrastructure deployed by Ansible
3. The Chef Automate and Chef Server deployment scripts are used for setting up a Chef environment, which would be replaced by AWX/Tower in an Ansible-only environment
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There are no external dependencies or integrations not visible in the repository
6. The migration goal is to standardize on Ansible while maintaining the same functionality and security posture
7. The hardcoded credentials in the setup scripts are for demonstration purposes only and would be replaced with secure credential management in production