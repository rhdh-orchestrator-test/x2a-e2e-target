# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a small set of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing with Ansible deployments. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing primarily on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-verification**:
    - Description: InSpec tests for verifying HTTPS website deployment with proper SSL/TLS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS content verification, SSL/TLS protocol security checks

- **ssh-security-profile**:
    - Description: InSpec compliance profile for SSH security configuration with STIG alignment
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, CCI compliance mapping, STIG alignment

- **chef-automate-deployment**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script with Chef commands
    - Key Features: User creation, organization setup, system configuration

- **chef-server-deployment**:
    - Description: Deployment script for Chef Infra Server (without Automate)
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script with Chef commands
    - Key Features: User creation, organization setup, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `website_https.yml`: Ansible playbook for deploying a secure HTTPS website with Apache
- `poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability in Apache
- `index.html`: Sample HTML file for website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Ansible Molecule with Testinfra for infrastructure testing
  - **Option 2**: Convert InSpec tests to Ansible assert tasks
  - **Option 3**: Use community.general.inspec module to continue using InSpec tests with Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline-based automation

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the HTTPS configuration:
  - Disable vulnerable protocols (SSL3, TLS 1.0, TLS 1.1)
  - Enable only TLS 1.2 as shown in the poodle_fix.yml playbook
  - Maintain proper certificate generation and configuration

- **SSH Security**: Preserve the SSH security controls:
  - Maintain the prohibition of root login via SSH
  - Preserve STIG compliance requirements

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL/TLS certificate references should use secure storage
  - Count of credentials detected:
    - chef-automate-deployment: 3 credentials (username, password, organization name)
    - chef-server-deployment: 3 credentials (username, password, organization name)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks may require learning new testing approaches and syntax.
  - Mitigation: Use Ansible's assert module or Molecule with Testinfra for similar functionality.

- **Compliance Reporting**: Chef InSpec provides built-in compliance reporting that needs to be replicated in Ansible.
  - Mitigation: Consider using Ansible Automation Platform's compliance capabilities or integrate with third-party compliance tools.

- **User and Organization Management**: The Chef server user and organization management needs to be replaced with equivalent Ansible inventory and AAA mechanisms.
  - Mitigation: Use Ansible Automation Platform's RBAC or integrate with external identity providers.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-compatible testing frameworks.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks for deploying Ansible Automation Platform or AWX.

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already in the target format and may only need minor adjustments.
3. The team has expertise in both Chef InSpec and Ansible to facilitate the migration.
4. There are no external dependencies or integrations not visible in the repository.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.
6. The migration will maintain the same level of security compliance as the original implementation.
7. The Test Kitchen configuration is used primarily for development and testing, not for production deployments.