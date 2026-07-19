# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is focused on two main components:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for verifying compliance and security

Additionally, there are Chef Automate and Chef Infra Server setup scripts that need to be migrated to Ansible.

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single engineer to complete the migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: A set of Ansible playbooks and Chef InSpec tests for configuring and validating HTTPS websites
    - Path: chef-and-ansible
    - Technology: Mixed (Ansible playbooks with Chef InSpec tests)
    - Key Features: HTTPS configuration, SSL certificate generation, compliance testing with InSpec

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef infrastructure
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring HTTPS websites with Apache, self-signed certificates, and virtual hosts. Can be directly used in the Ansible migration with minimal changes.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities by enforcing TLS 1.2 and disabling older protocols. Can be directly used in the Ansible migration with minimal changes.
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment. Can be directly used in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration, port 443 listening, and proper TLS protocols. Needs to be converted to Ansible testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configurations, specifically that root login is disabled. Needs to be converted to Ansible testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be replaced with Ansible playbooks for infrastructure setup.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be replaced with Ansible playbooks for infrastructure setup.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Keep InSpec as a standalone tool and call it from Ansible using the command module
  - Option 4: Migrate to Ansible Compliance as Code using DISA STIG or CIS roles

- **Test Kitchen with Vagrant**: Replace with Ansible Molecule for testing infrastructure

- **Apache 2.4.41**: Maintain the same version requirements in Ansible playbooks or update to newer versions if appropriate

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Preserve the same SSL/TLS configurations in the Ansible playbooks, consider updating to include TLS 1.3 support.

- **Self-signed Certificates**: The current implementation generates self-signed certificates using OpenSSL.
  - Migration approach: Maintain the same approach or enhance with Let's Encrypt integration for production environments.

- **SSH Root Login Restrictions**: InSpec tests verify that SSH root login is disabled.
  - Migration approach: Ensure Ansible playbooks enforce the same SSH security configurations and include verification steps.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing mechanisms.
  - Mitigation strategy: Use Ansible's assert module for basic tests, and consider maintaining InSpec for complex compliance testing if needed.

- **Chef Automate Deployment**: Replacing Chef Automate with equivalent Ansible functionality.
  - Mitigation strategy: Identify the specific features of Chef Automate being used and map to Ansible Tower/AWX or other Ansible-compatible tools.

- **Compliance Automation**: Ensuring that the compliance testing capabilities of InSpec are adequately replaced in the Ansible solution.
  - Mitigation strategy: Evaluate Ansible's built-in capabilities for compliance checking and consider integrating with specialized compliance tools if needed.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk, already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (chef-and-ansible/tests/*.rb): Moderate complexity, requires conversion to Ansible testing mechanisms
3. **Chef Infrastructure Setup** (setup-automate/*.sh): High complexity, requires replacing Chef-specific infrastructure with Ansible alternatives

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. The security configurations are examples and may need to be enhanced for production use.
4. The Chef Automate and Chef Infra Server setup scripts are used for demonstration purposes and may not reflect production deployment practices.
5. There are no external dependencies or integrations beyond what is explicitly defined in the repository.
6. The migration will maintain the same functionality but using Ansible-native approaches where possible.
7. The hardcoded credentials in the setup scripts are for demonstration purposes only and would be replaced with secure credential management in a production environment.
8. The InSpec tests are intended to verify both the configuration and security compliance of the systems.