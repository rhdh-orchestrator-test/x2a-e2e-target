# MIGRATION FROM CHEF/ANSIBLE HYBRID TO ANSIBLE

## Executive Summary

This repository contains a hybrid environment with both Chef and Ansible components. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with a few Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server setup scripts. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains a hybrid Chef/Ansible environment that needs individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening for Apache SSL configuration

- **InSpec Tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTP response testing, SSL protocol validation, SSH configuration compliance checks

- **Chef Automate Setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **Chef Server Setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Simple HTML template used in the website_https playbook - can be reused as-is
- `README.md`: Documentation files - will need updates to reflect Ansible-only approach

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate with pytest-ansible for more complex test scenarios

- **Test Kitchen with Vagrant**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Consider GitHub Actions or other CI/CD tools for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open-source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline automation

### Security Considerations

- **SSL Configuration**: The current implementation properly disables SSLv3 and enables only TLSv1.2. This security practice should be maintained in the migrated solution.
- **SSH Hardening**: The InSpec profile checks for secure SSH configuration (disabling root login). Ensure this security check is maintained in the Ansible-native testing.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider implementing Let's Encrypt integration for production environments.
- **Hardcoded Credentials**: The Chef server setup scripts contain hardcoded credentials. These should be moved to Ansible Vault or another secrets management solution.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require understanding the compliance requirements and implementing equivalent checks using Ansible's testing frameworks.
  - Mitigation: Use ansible.builtin.assert or ansible.builtin.fail modules to implement compliance checks directly in playbooks, or use Molecule for more comprehensive testing.

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting capabilities with Ansible equivalents.
  - Mitigation: Consider implementing compliance reporting using Ansible Automation Platform or integrating with tools like Prometheus and Grafana for monitoring and reporting.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format. May need minor adjustments for best practices.
2. **Testing Framework**: Migrate from Test Kitchen and InSpec to Ansible Molecule or equivalent.
3. **Chef Automate/Server Setup**: Replace with Ansible playbooks for setting up Ansible Automation Platform or AWX.

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment.
2. The target environment is Ubuntu 20.04, but the solution should be adaptable to other distributions.
3. The current implementation uses Vagrant for local testing, but the production environment could be different.
4. There are no external dependencies or integrations not visible in the repository.
5. The security requirements demonstrated by the InSpec tests (HTTPS configuration, SSH hardening) are critical and must be maintained in the migrated solution.
6. The Chef Automate and Chef Infra Server setup scripts are used for demonstration purposes and not critical production infrastructure.