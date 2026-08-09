# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec profiles and Ansible playbooks that are used for compliance automation and infrastructure configuration. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **automate-deployment**:
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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Simple HTML file used as a test page for the web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Migrate to Ansible Molecule with Testinfra for testing
  - Option 2: Use the ansible-test framework with custom Python test modules
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Or continue using Test Kitchen with the Ansible verifier plugin

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible roles for configuration management
  - Consider migrating to Ansible Tower/AWX for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should preserve:
  - Self-signed certificate generation
  - Proper SSL protocol configuration (disabling SSLv3, enabling TLSv1.2)
  - Ensure certificate paths and permissions are maintained

- **SSH Security**: The InSpec profile checks SSH root login configuration. Migration should:
  - Maintain compliance with STIG requirements
  - Preserve the security checks in the new testing framework

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to equivalent Ansible/Python testing frameworks will require careful mapping of assertions and resources.
  - Mitigation: Create a mapping document for InSpec resources to Ansible/Testinfra equivalents

- **Compliance Reporting**: If Chef Automate is being used for compliance reporting, an alternative solution will be needed.
  - Mitigation: Evaluate Ansible Tower/AWX compliance reporting capabilities or integrate with third-party compliance tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-compatible testing
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires creating equivalent Ansible roles for Chef server deployment or finding alternative solutions

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production, based on the README content.
2. The Chef InSpec tests are used alongside Ansible for compliance verification rather than as part of a larger Chef ecosystem.
3. The deployment scripts are examples and not actively used in production environments.
4. The hardcoded credentials in the deployment scripts are example values and not actual production credentials.
5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
6. The migration goal is to standardize on Ansible rather than maintain a hybrid Chef/Ansible environment.
7. There are no external dependencies or integrations not visible in the repository.
8. The SSL and SSH configurations are based on standard security practices and don't have custom organizational requirements.