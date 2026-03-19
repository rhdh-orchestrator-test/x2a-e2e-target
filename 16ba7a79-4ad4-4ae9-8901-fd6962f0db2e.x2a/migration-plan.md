# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, primarily involving:

1. Chef InSpec test profiles that need to be migrated to Ansible-compatible testing frameworks
2. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
3. Existing Ansible playbooks that need to be reviewed and potentially refactored

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **2-3 weeks** for a small team, as the repository primarily contains demonstration code rather than production infrastructure.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `index.html`: Simple HTML file used for testing web server deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Integrate with pytest-ansible for more complex testing scenarios

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for environment provisioning and testing
  - Option 2: Use simple Vagrant configurations directly with Ansible

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower
  - Option 2: Use GitLab CI/CD with Ansible
  - Option 3: Use Jenkins with Ansible

### Security Considerations

- **SSL Configuration**: The current playbooks configure Apache with TLSv1.2 and disable older protocols. Ensure the migrated Ansible roles maintain or enhance this security posture.
  
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Ensure this security check is maintained in the migrated testing framework.

- **Credentials in Scripts**: The deployment scripts contain hardcoded credentials. Migrate these to Ansible Vault or another secure secret management solution.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks will require mapping InSpec resources to equivalent Ansible modules or custom modules.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules and develop reusable test patterns.

- **Compliance Reporting**: If compliance reporting is a key requirement, ensure the Ansible solution provides equivalent capabilities to Chef InSpec.
  - Mitigation: Evaluate Ansible Automation Platform's compliance capabilities or integrate with third-party compliance tools.

- **Chef Server Functionality**: If Chef Server functionality is required, ensure equivalent capabilities exist in the Ansible solution.
  - Mitigation: Map Chef Server features to Ansible Automation Platform features and identify any gaps.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Review and refactor these playbooks first as they are already in Ansible format and will be the easiest to migrate.

2. **Chef InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-native testing frameworks to ensure continued compliance validation.

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these to Ansible playbooks for infrastructure deployment.

### Assumptions

1. The repository is primarily for demonstration purposes rather than production infrastructure, based on the README.md content.

2. The primary goal is to showcase compliance automation with Ansible, so maintaining the compliance testing capabilities is a priority.

3. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

4. The current implementation uses self-signed certificates, which may not be suitable for production environments.

5. The deployment scripts contain hardcoded credentials, which would need to be secured in a production environment.

6. The repository demonstrates the integration of Chef InSpec with Ansible, but the goal is to migrate to a pure Ansible solution.

7. The existing Ansible playbooks are functional and follow best practices, but may benefit from refactoring to use roles and collections.